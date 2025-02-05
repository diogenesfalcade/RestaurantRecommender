import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sqlalchemy import create_engine
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

conn_string = "postgresql://postgres:manager@localhost:5432/postgres"
db = create_engine(conn_string)

query = "select * from ta_features_expanded"
    
df = pd.read_sql(query, db)

location_encoder = LabelEncoder()
df["location_id"] = location_encoder.fit_transform(df["location_id"])

scaler = MinMaxScaler()
numeric_features = ["ranking", "rating_geral", "rating_comida", "rating_servico", "rating_valor"]
df[numeric_features] = scaler.fit_transform(df[numeric_features])

# Converter tudo para float32 para o PyTorch
df = df.astype("float32")

class RestaurantDataset(Dataset):
    def __init__(self, df):
        self.features = torch.tensor(df.drop(columns=["location_id", "nome"]).values, dtype=torch.float32)
        self.labels = torch.randint(0, 2, (len(df), 1), dtype=torch.float32) 
    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


dataset = RestaurantDataset(df)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

class FactorizationMachine(nn.Module):
    def __init__(self, n_features, k):
        super(FactorizationMachine, self).__init__()
        self.linear = nn.Linear(n_features, 1)  # Termo linear
        self.v = nn.Parameter(torch.randn(n_features, k) * 0.01)  # Termo de interação

    def forward(self, x):
        linear_term = self.linear(x)
        interactions = 0.5 * torch.sum(
            torch.pow(torch.matmul(x, self.v), 2) - torch.matmul(torch.pow(x, 2), torch.pow(self.v, 2)), 
            dim=1, keepdim=True
        )
        return torch.sigmoid(linear_term + interactions)  # Saída entre 0 e 1

# Instanciar o modelo
n_features = df.shape[1] - 2  # Número de colunas (removendo "location_id" e "nome")
model = FactorizationMachine(n_features=n_features, k=10)

# Definir função de perda e otimizador
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)


# Loop de treinamento
num_epochs = 10

for epoch in range(num_epochs):
    for batch in dataloader:
        features, labels = batch

        # Forward
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, labels)

        # Backward
        loss.backward()
        optimizer.step()

    print(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}')
