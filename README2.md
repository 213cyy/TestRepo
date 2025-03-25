
 大家好,
 这个仓库里存放的是一些
 试图使用 OpenGL 渲染魔兽争霸游戏的 python 代码

 我希望被 review 的地方主要是在
 这个Ground的目录下的GroundDefault的这个 python 文件

 这个文件会解析一个魔兽地形的一个二进的文件
 然后渲染出来一个魔兽的地图
 这个文件中有很多渲染用的代码,
 但都不是我想要被review的地方.

 我想被review的地方就两个地方

 一个是读取并解析这个二进的文件的代码部分
 就是文件240行之前的部分
 这部分中有个叫 MapInfo 的 class
 这个 class 用于转录了文件里的地形数据,
 并且进一步处理,整理出渲染所用的数据做为实例的属性
 最终这个 class 的实例会丢到其他对象里面进行接下来的渲染

 第二个希望被review一下的地方就是这个模块的运行流程
 就是文件最后765行之后的部分
 从这里这个模块可以直接运行,
 但是我觉得我的的运行需求比较特别.
 所以这段运行代码让我写得很别扭
 也许有更简单的处理,但我似乎已经弥足深陷,难以自拔了
 
 我仓库里的所有代码都是初级原材料阶段
 勉勉强强可以算为半成品
 而且我的系统是 win7 , python 是 3.8 的
 项目的发布,更新和维护都没有意义.
 所以编程风格的统一,注释规范,以及 cache 文件 等等,我都不在意
 但是我希望变量,函数的命名质量能高一点


#################################################

 
 先说一下这个项目的两种运行方式
 可以看到,这个项目的工作目录下有一个main.py的python文件,做为项目的总的入口.
 然后还有一些文件夹,这些文件夹下都有一些自己各自的python文件

 如果我直接运行main.py这个文件的话
 它实例化一个APP的对象之后就开始 运行这个实例
 实例运行的时候会根据默认的配置将所有其他文件夹中的所有子模块全部导进来
 然后全部渲染出来, 这是一种运行方式


 另外这个项目可以看成是一个 opengl 的学习,练习,演示的一个项目
 在各个子文件夹下的 python 文件,可以看成是一个个相对独立的子模块,
 按照我的设计,他们大多数是用来实现的一个具体的渲染套路,
 比如说可以演示一种技术概念,演示一些函数的使用,或是实现一类特别的对象,
 他们是 OpenGL 在学习当中的各种概念,套路的练习集合,他们都是可以直接运行的
 
 如果要单独运行这些子模块的话
 他们会先从项目根目录下导入这个main.py文件
 实例化一个app,然后按照子模块的配置文件,对这个app进行配置
 然后再运行
 目的就是可以渲染出一个最小的演示系统,把默认初始化的一些函数清零
 然后只导入正在运行的当前的子模块的内容
 最终就会仅对本模块的内容进行渲染,
 就是用 main.py 渲染出来了一个舞台,主角是当前模块的内容
 其他的文件夹下的子模块,就不导入和渲染了
 
 
 这样可以提高运行速度,减少资源占用,渲染的东西少了,突出了重点,而且便于调试演示
 调试的时候.因为如果我对子模块就行修改,或是打上断点,
 然后就可以直接点运行子模块,这样可以直接运行修改后的内容或是,在断点处断下
 
 
 总结一下就是,我这个项目有两种运行流程.
 为了实现者两种运行方式,我需要在每个子模块的开头和入口代码中实现两种导入方式
 模块开始要加入一个if -- else 这么一大段东西,
 入口代码中还要先配置一下路径然后再导入
 

 我这么导入还有一种更复杂的情况
 像这个文件夹units,下面有一个unit default的python文件,然后这有个cube和nounit这两个文件夹
 这两文件夹下的python文件又要导入 那个unit default 那个py文件
 也就是说 子模块处理导入工作目录的 main.py 文件,还得导入units文件夹下的unit_default.py文件
 总之整个导入的过程让我觉得是异常的麻烦


 我觉得这样的代码非常的臃肿,不优雅.
 让我觉得这些代码看起来很不很不专业,很业余
 所以想被 review 一下这两种运行流程
 看看是不是还有更好的实现方式 

##########################################

 上面说的是导入模块和运行的问题
 还有一部分我想被 review 的是 ground_default.py 中的前一部分代码
 这部分代码就是这两个class的实现部分
 一个是mapinfo 一个是  tilecorner

 mapinfo这个class呢
 实际上就是完成了从一个二进的魔兽地形文件当中
 读取地图属性数据
 并把地图属性转写设置到我这个 mapinfo 实例的属性当中去
 这个二进制文件,除了记录了地图属性,
 还有一个二进制的 array 记录的是地图上一些地形关键点的地形数据
 mapinfo 会把每个地形关键点的数据转化为 tilecorner 这个class
 然后把所有地形点的 tilecorner 存在一个python list中, 做为mapinfo自己的一个属性
 mapinfo 下的唯一的一个函数load_file_data就完成了上述的这两个工作
 在 load_file_data 中我使用struct这module去解包二进制数据
 我想知道一些我这个解包流程的代码是否是正常.
 我感觉看上去很不专业.
 特别是这个地方.我通过zip,和 setattr 一口气对实例设置了很多的解包数据.
 这种方式写起来比较紧凑
 但是对于linter程序来说,它是不是应该不知道这个对象有这么些属性
 尽管我不是很在意这一点.
 但我也想知道这样弄好不好.


 当所有地图的原始数据都载入之后, 跟着就是三个循环
 因为可以认为每4个 tilecorner 会组成一个tile
 那这三个循环就是按照一些应用于 tile 的逻辑去填充一些空的 list
 这些填充出来的 list 做为 mapinfo的属性被记录下来,
 可以认为是一种输出.是一些给后续渲染所准备的数据.

 在整个过程中我感到我的代码逻辑不够清晰,虽然可能也没有更好的实现
 主要表现在,我都在不停的去访问各个 tilecorner 的属性数据,
 然后不停的给各个tilecorner 添加,或是更新属性数据
 尤其在 tilecorner 中还有一个函数 init_position 也是在更新 tilecorner 的属性
 这个函数其实就被调用了一次,感觉也是非常的鸡肋

上述的内容就是全部我想被review的代码部分
实际上内容并不多,而且很简单,都是些一般性的问题
对于代码业务上的逻辑,不需要被review.




## XXXXXXXXXXXX

0. Requires Visual Studio 17.7 or higher (C++20 modules)
3. Run vcpkg/bootstrap-vcpkg.bat
4. Add an environment variable to your system:

## YYYYYYYYYYYY

Want to help with the development of HiveWE? Below is a list of features that you could implement. You can try one of these or just add something else you feel like HiveWE should have. Any contributions are welcome!

- Being able to change forces/teams
- Changing map sizes/camera bound
- Ramp editing with the terrain palette