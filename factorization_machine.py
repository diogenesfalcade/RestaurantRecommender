import torch
import torch.nn as nn

class FactorizationMachine(nn.Module):
    def __init__(self, n_features, k):
        super(FactorizationMachine, self).__init__()
        self.linear = nn.Linear(n_features, 1)
        self.v = nn.Parameter(torch.randn(n_features, k) * 0.01)

    def forward(self, x):
        linear_term = self.linear(x)
        interactions = 0.5 * torch.sum(
            torch.pow(torch.matmul(x, self.v), 2) - torch.matmul(torch.pow(x, 2), torch.pow(self.v, 2)), dim=1, keepdim=True
        )
        return torch.sigmoid(linear_term + interactions)

# Exemplo de entrada de dados
X_train = torch.randn(1000, 120)  # Suponha 120 features
y_train = torch.randint(0, 2, (1000, 1)).float()

# Treinamento
model = FactorizationMachine(n_features=120, k=10)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(10):
    optimizer.zero_grad()
    y_pred = model(X_train)
    loss = criterion(y_pred, y_train)
    loss.backward()
    optimizer.step()
    print(f'Epoch {epoch}, Loss: {loss.item()}')
