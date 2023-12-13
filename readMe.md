
## 项目简介

- **项目名** Bilibili弹幕机
- **实现方式**
  - 后端通过websocket获取弹幕数据
  - 前端使用pyqt设计界面(设置界面、显示界面和托盘界面)
  - 通过config.json配置文件格式化输出弹幕信息

## 注意事项

- **适用平台** 
  > windows11，非windows平台暂时未测试。
    Win10上可能会出现显示窗口不透明，正在适配。
- **弹幕信息脱敏** 
  > 正常现象，B站9月份后服务器更新，未登录的用户接受到的弹幕信息是脱敏的（用户名为*号）。
    ~~可通过修改config中的UID参数和cookie参数尝试获取~~。实测12月9号之前可行，12月10号后
    即便获取到token后还是不行。
- **config文件丢失**
  > 解决办法: 可尝试重启程序，程序会检查config文件是否存在并生成。或者将TempConfig内的config.json文件
    放入到程序工作目录里。以上两种方法失效，可尝试从仓库里复制config.json文件。
- **开发接口**
  > BiliWebSocket目录里BiliSocket类和dependencies.py依赖文件可单独拉出来使用，前提是要修改一部分参数。
    BiliSocket类基于Websocket，结合B站官方的协议包格式，异步获取直播弹幕数据
   （此类使用的api接口非官方提供，官方提供的api接口请看[官方开发文档](https://open-live.bilibili.com/document/)
    不过官方提供的接口，只能通过主播身份码获取到直播弹幕数据）。
    要开发其他界面（Electron、 html等）可直接使用这个类，获取弹幕数据。
- **得意黑字体**
  > 各ui窗体均使用得意黑字体，使用者需先下载得意黑字体，否则窗口字体可能会显示部分错误，
    得意黑字体开源地址 [得意黑](https://github.com/atelier-anchor/smiley-sans)
- **免责声明**
  > 本软件仅供学习交流使用，不得用于任何商业用途。
    作者不对因本软件的误用、滥用或非法使用而导致的任何损害或责任承担责任。
    作者保留在任何时候修改本免责声明的权利。更新后的免责声明将在软件发布后生效。
    本免责声明适用于本软件的所有版本。
  