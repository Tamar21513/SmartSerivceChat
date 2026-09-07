import torch
import torch.nn as nn
import math
class MultiHeadAttention(nn.Module):
    # Initialize the query/key/value/output projection layers for multi-head attention
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
    # Compute scaled dot-product attention scores, apply the optional mask, and weight the values
    def scaled_dot_product_attention(self, Q, K, V, mask = None):
        attn_scores = torch.matmul(Q, K.transpose(-1, -2)) / math.sqrt(self.d_k) #D_K
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, -1e9) 
        attn_probs = torch.softmax(attn_scores, dim = -1)
        output = torch.matmul(attn_probs, V)
        return output
    # Reshape a tensor to split its last dimension into (num_heads, d_k) for parallel attention heads
    def split_head(self,x):
        batch_size, seq_length, d_model = x.size()
        return  x.view(batch_size, seq_length, self.num_heads, self.d_k).transpose(1, 2)
    # Merge the separate attention heads back into a single d_model-sized dimension
    def combine_heads(self, x):
        batch_size, _, seq_length,d_k = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, seq_length, self.d_model)
    # Project Q/K/V, split into heads, run attention, then recombine and project the output
    def forward(self, Q, K, V, mask = None):
        batch_size = Q.size(0)
        q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        k = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        v = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        attn_output = self.scaled_dot_product_attention(q, k, v, mask)
        output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.W_o(output)
    

class PositionWiseFeedForward(nn.Module):
    # Initialize the two linear layers and GELU activation used for the feed-forward block
    def __init__(self, d_model, d_ff):
        super(PositionWiseFeedForward, self).__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.activation = nn.GELU()
    # Apply the two-layer feed-forward transformation with GELU activation in between
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
    # Initialize the self-attention and feed-forward sub-layers with their layer norms and dropout
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    # Apply self-attention with a residual connection, then the feed-forward block with another residual connection
    def forward(self, x, mask):
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        return x
