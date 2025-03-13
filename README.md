# 高天 code review 投稿
gaotian code review post

评论草稿:  
这是我写的用opengl渲染war3地图的一些程序,  
希望高神能帮我review一下.  
https://github.com/213cyy/TestRepo/blob/master/pywar3/ground/ground_default.py
中 240 行之前 735 行之后的部分  
这部分和渲染无关,一部分完成了二进制文件数据的载入和解析.另外一部分则是项目的启动代码.  
我希望得到在 项目运行流程 和 数据组织 方面的指导和建议,谢谢!  
这里有关于 项目 和 上述程序大致逻辑 的说明视频:  
[有热心的网友能帮我 review 一下我的代码么?](https://www.bilibili.com/video/BV1LvRWYzEKT)    
https://www.bilibili.com/video/BV1LvRWYzEKT  
希望水友支持我中选!谢谢!


## 项目介绍
paperwar3 or pyperwar3

## 图片

- Edit the terrain
![HiveWE Screenshot](/HiveWE.png)
- Advanced Object Editor
![HiveWE Screenshot](/ObjectEditor.png)

## Build Instructions

0. Requires Visual Studio 17.7 or higher (C++20 modules)
1. Clone HiveWE somewhere 
`git clone https://github.com/stijnherfst/HiveWE.git`
2. Clone [vcpkg](https://github.com/microsoft/vcpkg) somewhere central (eg. "C:/")
`git clone https://github.com/Microsoft/vcpkg.git`
3. Run vcpkg/bootstrap-vcpkg.bat
4. Add an environment variable to your system:

## 问题

Want to help with the development of HiveWE? Below is a list of features that you could implement. You can try one of these or just add something else you feel like HiveWE should have. Any contributions are welcome!

- Being able to change forces/teams
- Changing map sizes/camera bound
- Ramp editing with the terrain palette
- Making HiveWE run faster
- An FDF frame editor
- Text colorizer
- Advanced terrain editing tools (e.g. flood fill, magic wand selection)
- Or any other functionality you think would be cool