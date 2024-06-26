
import torch 
import torch.nn as nn
import torchvision.transforms as transforms











def conv3x3(in_channels,out_channels,stride=1):
    return nn.Conv2d(in_channels,out_channels,kernel_size=3,stride=stride,padding=1,bias=False)


class ResidualBlock(nn.Module):
    def __init__(self,in_channels,out_channels,stride=1,downsampling=None):
        super(ResidualBlock,self).__init__()
        self.conv1 = conv3x3(in_channels,out_channels,stride)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(in_channels,out_channels)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.downsample = downsampling
    
    def forward(self,x):
        residual = x.clone()
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        if self.downsample :
            self.downsample(x)
        out += residual 
        out = self.bn2(out)



class Resnet(nn.Module):
    def __init__(self,block,layers,num_classes =10):
        super(Resnet,self).__init__()
        self.in_channels = 16
        self.conv = conv3x3(3,16)
        self.bn = nn.BatchNorm2d(16)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(block,16,layers[0])
        self.layer2 = self._make_layer(block,32,layers[1],stride=2)
        self.layer3 = self._make_layer(block,64,layers[2],stride=2)
        self.avg_pool = nn.AvgPool2d(8)
        self.fc = nn.Linear(64,num_classes)
    
    def _make_layer(self,block,out_channels,blocks,stride=1):
        downsample = None 
        if (stride != 1)or (self.in_channels != out_channels):
            downsample = nn.Sequential(conv3x3(self.in_channels,out_channels,stride),nn.BatchNorm2d(out_channels))
        layers = []
        layers.append(block(self.in_channels,out_channels,stride,downsample))
        self.in_channels = out_channels
        for i in range(1,blocks):
            layers.append(block(out_channels,out_channels))
        return nn.Sequential(*layers)
    
    def forward(self,x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avg_pool(x)
        x = x.view(x.size(0),-1)
        x = self.fc(x)
        return x



model = Resnet(ResidualBlock,[2,2,2]).to(device)