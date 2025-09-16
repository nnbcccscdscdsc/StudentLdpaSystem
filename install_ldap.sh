#!/bin/bash

# LDAP服务器安装和配置脚本
# 适用于Ubuntu 22.04

echo "=== 开始安装OpenLDAP服务器 ==="

# 1. 更新包管理器
echo "更新包管理器..."
sudo apt update

# 2. 安装OpenLDAP和相关工具
echo "安装OpenLDAP服务器和工具..."
sudo apt install -y slapd ldap-utils

# 3. 重新配置slapd（设置管理员密码和域名）
echo "配置LDAP服务器..."
sudo dpkg-reconfigure slapd

# 4. 启动并启用LDAP服务
echo "启动LDAP服务..."
sudo systemctl start slapd
sudo systemctl enable slapd

# 5. 检查服务状态
echo "检查LDAP服务状态..."
sudo systemctl status slapd

# 6. 用于查询 LDAP 目录中的数据
# -b 表示 基本搜索（Base DN），它指定了 LDAP 查询的起点
# -D 参数指定了绑定 DN（Distinguished Name），即用来进行身份验证的用户的 DN。

# 这意味着你用 cn=admin,dc=szuldpa-edu,dc=com 作为身份验证的用户来执行查询。
sudo ldapsearch -x -b "dc=szuldpa-edu,dc=com" -D "cn=admin,dc=szuldpa-edu,dc=com" -W


echo "=== LDAP服务器安装完成 ==="
echo "接下来需要配置LDAP数据库结构..."
