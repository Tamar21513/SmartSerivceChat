import torch
import torch.nn as nn

class MyQAMatchingTransformerEmbeddings(nn.Module):
    def __init__(self, vocab_size=30522, hidden_dim=768, max_position_embeddings=512):
        super().__init__()
        self.my_Embedding=nn.Embedding(vocab_size, hidden_dim)
        self.my_position_Embedding=nn.Embedding(max_position_embeddings,hidden_dim)
        self.LayerNorm=nn.LayerNorm(hidden_dim)
        self.Dropout=nn.Dropout(p=0.1)

    def forward(self,input_ids, token_weights=None):
        word_vec= self.my_Embedding(input_ids)

        if token_weights is not None:
            word_vec = word_vec * token_weights.unsqueeze(-1)

        seq_length = input_ids.size(1)
        word_pos=torch.arange(seq_length,device=input_ids.device)
        pos_vecs = self.my_position_Embedding(word_pos)
        my_token_embedding=word_vec+pos_vecs
        my_token_embedding=self.LayerNorm(my_token_embedding)
        my_token_embedding=self.Dropout(my_token_embedding)
        return my_token_embedding