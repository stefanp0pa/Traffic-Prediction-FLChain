import torch
import torch.nn as nn
import torch.nn.functional as F

class cheb_conv(nn.Module):

    def __init__(self, K, cheb_polynomials, in_channels, out_channels):
        super(cheb_conv, self).__init__()
        self.K = K
        self.cheb_polynomials = cheb_polynomials
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.DEVICE = cheb_polynomials[0].device
        self.Theta = nn.ParameterList([nn.Parameter(torch.FloatTensor(in_channels, out_channels).to(self.DEVICE)) for _ in range(K)])

    # sum i=0...k-1  X*theta(i)*Ti(L˜)
    # Ti -> chebysev
    # L˜ = 2L/lambda_max - I
    def forward(self, x):
        batch_size, num_of_vertices, in_channels, num_of_timesteps = x.shape
        outputs = []
        for time_step in range(num_of_timesteps):
            graph_signal = x[:, :, :, time_step]
            output = torch.zeros(batch_size, num_of_vertices, self.out_channels).to(self.DEVICE)  # (b, N, F_out)
            for k in range(self.K):
                T_k = self.cheb_polynomials[k]
                theta_k = self.Theta[k]
                aux = graph_signal.permute(0, 2, 1).matmul(T_k)
                rhs = aux.permute(0, 2, 1)
                output = output + rhs.matmul(theta_k)
            outputs.append(output.unsqueeze(-1))
        return F.relu(torch.cat(outputs, dim=-1))


class GCN_block(nn.Module):

    def __init__(self, in_channels, K, nb_chev_filter, nb_time_filter, time_strides, cheb_polynomials):
        super(GCN_block, self).__init__()
        self.cheb_conv = cheb_conv(K, cheb_polynomials, in_channels, nb_chev_filter)
        self.time_conv = nn.Conv2d(nb_chev_filter, nb_time_filter, kernel_size=(1, 3), stride=(1, time_strides), padding=(0, 1))
        self.residual_conv = nn.Conv2d(in_channels, nb_time_filter, kernel_size=(1, 1), stride=(1, time_strides))
        self.ln = nn.LayerNorm(nb_time_filter)

    # s_gcn = cheb(x)
    # time_conv = conv(s_gcn)
    # x_residual = normalization(Relu(conv(X) + time_conv))

    def forward(self, x):
        spatial_gcn = self.cheb_conv(x)
        time_conv_output = self.time_conv(spatial_gcn.permute(0, 2, 1, 3))
        x_residual = self.residual_conv(x.permute(0, 2, 1, 3))
        x_residual = self.ln(F.relu(x_residual + time_conv_output).permute(0, 3, 2, 1)).permute(0, 2, 3, 1)
        return x_residual


class GCN(nn.Module):

    def __init__(self, DEVICE, nb_block, in_channels, K, nb_chev_filter, nb_time_filter, time_strides, cheb_polynomials_layer_1, cheb_polynomials,num_for_predict, len_input):
        super(GCN, self).__init__()

        self.Layer1 = nn.ModuleList([GCN_block(in_channels, K, nb_chev_filter, nb_time_filter, time_strides, cheb_polynomials_layer_1)])
        self.BlockList = nn.ModuleList([GCN_block(nb_time_filter, K, nb_chev_filter, nb_time_filter, 1, cheb_polynomials) for _ in range(nb_block-1)])
        self.final_conv = nn.Conv2d(int(len_input/time_strides), num_for_predict, kernel_size=(1, nb_time_filter))
        self.DEVICE = DEVICE
        self.to(DEVICE)

    # get the final X
    # output = conv(X)
    def forward(self, x):

        for block in self.Layer1:
            x = block(x)

        for block in self.BlockList:
            x = block(x)

        output = self.final_conv(x.permute(0, 3, 1, 2))[:, :, :, -1].permute(0, 2, 1)
        return output