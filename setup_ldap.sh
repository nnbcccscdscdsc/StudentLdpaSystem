#!/bin/bash

# LDAP服务器配置脚本
# 配置数据库结构和导入数据

echo "=== 开始配置LDAP数据库 ==="

# 1. 检查LDAP服务是否运行
echo "检查LDAP服务状态..."
if ! systemctl is-active --quiet slapd; then
    echo "启动LDAP服务..."
    sudo systemctl start slapd
fi

# 2. 导入LDIF配置文件
echo "导入LDAP配置..."
sudo ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f ldap_config.ldif

# 3. 验证导入结果
echo "验证LDAP数据..."
sudo ldapsearch -x -b "dc=example,dc=com" -D "cn=admin,dc=example,dc=com" -W

echo "=== LDAP配置完成 ==="
echo "现在可以开始创建Web登录界面了"
