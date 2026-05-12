import torch
import torch.nn as nn
import math
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads 
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model) 
    def scaled_dot_product_attention(self, Q, K, V, mask = None):
        attn_scores = torch.matmul(Q, K.transpose(-1, -2)) / math.sqrt(self.d_k) #D_K
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, -1e9) 
        attn_probs = torch.softmax(attn_scores, dim = -1)
        output = torch.matmul(attn_probs, V)
        return output
    def split_head(self,x):
        batch_size, seq_length, d_model = x.size()
        return  x.view(batch_size, seq_length, self.num_heads, self.d_k).transpose(1, 2)
    def combine_heads(self, x):
        batch_size, _, seq_length,d_k = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, seq_length, self.d_model)
    def forward(self, Q, K, V, mask = None):
        batch_size = Q.size(0)
        q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        k = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        v = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        attn_output = self.scaled_dot_product_attention(q, k, v, mask)
        output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.W_o(output)
    

class PositionWiseFeedForward(nn.Module):
    def __init__(self, d_model, d_ff):
        super(PositionWiseFeedForward, self).__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.activation = nn.GELU()
    def forward(self, x):
        return self.fc2(self.activation(self.fc1(x)))
    


#class PositionalEncoding(nn.Module):
#    def __init__(self, d_model, max_seq_length=514):
#        super().__init__()
#        self.pe = nn.Embedding(max_seq_length, d_model)
#    def forward(self, x):
#        seq_len = x.size(1)
#        positions = torch.arange(2, seq_len + 2, device=x.device).unsqueeze(0)
#        return x + self.pe(positions)
    

    
class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    def forward(self, x, mask):
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        return x
