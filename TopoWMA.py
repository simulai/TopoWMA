!pip install torch torchvision scikit-tda matplotlib

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sktda.diagrams import PersistenceDiagram
from sktda.metrics import wasserstein_distance

# 超参数设置 (道：可调而非常调)
config = {
    "tao_lambda": 0.1,  # 拓扑正则化强度
    "wuwei_threshold": 0.5,  # 无为而治的激活阈值
    "batch_size": 128,
    "latent_dim": 8,  # 潜在空间维度（八卦数）
    "epochs": 20
}

# 阴阳自编码器架构
class YinYangAE(nn.Module):
    def __init__(self):
        super().__init__()
        # 编码器（阴）
        self.encoder = nn.Sequential(
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, config["latent_dim"])
        )
        
        # 解码器（阳）
        self.decoder = nn.Sequential(
            nn.Linear(config["latent_dim"], 64),
            nn.ReLU(),
            nn.Linear(64, 256),
            nn.ReLU(),
            nn.Linear(256, 784),
            nn.Sigmoid()
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z), z

# 道德经正则化项
def dao_regularization(z):
    """计算潜在空间的拓扑复杂度（道可道非常道）"""
    # 将潜在空间转换为持久同调图
    diagram = PersistenceDiagram().fit_transform(z.detach().cpu().numpy())
    
    # 计算0维和1维拓扑特征的Wasserstein距离
    w0 = wasserstein_distance(diagram, 0)
    w1 = wasserstein_distance(diagram, 1)
    
    # 返回拓扑复杂度度量（无名之朴）
    return (w0 + w1) / 2

# 加载MNIST数据（万物之始）
transform = transforms.Compose([transforms.ToTensor()])
train_set = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_set, batch_size=config["batch_size"], shuffle=True)

# 初始化模型和优化器
model = YinYangAE()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# 训练循环（周行而不殆）
loss_history = []
for epoch in range(config["epochs"]):
    for data, _ in train_loader:
        x = data.view(-1, 784)
        optimizer.zero_grad()
        
        # 前向传播
        x_recon, z = model(x)
        
        # 计算重构损失（有名）
        recon_loss = nn.functional.mse_loss(x_recon, x)
        
        # 计算拓扑正则化（无名）
        topo_loss = dao_regularization(z)
        
        # 无为而治：动态调整正则化强度
        if topo_loss < config["wuwei_threshold"]:
            total_loss = recon_loss
        else:
            total_loss = recon_loss + config["tao_lambda"] * topo_loss
        
        # 反向传播
        total_loss.backward()
        optimizer.step()
        
        loss_history.append(total_loss.item())
    
    print(f"Epoch {epoch+1}: Loss={np.mean(loss_history[-100:]):.4f}")

# 可视化结果（执大象，天下往）
plt.figure(figsize=(12, 4))

# 损失曲线
plt.subplot(1, 3, 1)
plt.plot(loss_history)
plt.title("阴阳训练过程")
plt.xlabel("迭代")
plt.ylabel("总损失")

# 潜在空间可视化
with torch.no_grad():
    sample_data, _ = next(iter(train_loader))
    _, z = model(sample_data.view(-1, 784))
    z_tsne = TSNE(n_components=2).fit_transform(z.numpy())
    
plt.subplot(1, 3, 2)
plt.scatter(z_tsne[:,0], z_tsne[:,1], alpha=0.6)
plt.title("潜在空间分布")
plt.xlabel("阴")
plt.ylabel("阳")

# 重构示例
plt.subplot(1, 3, 3)
plt.imshow(x_recon[0].view(28,28).numpy(), cmap='gray')
plt.title("重构结果")
plt.axis('off')

plt.tight_layout()
plt.show()