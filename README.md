# 学生LDAP系统

基于OpenLDAP和Flask构建的现代化学生信息管理系统，提供安全的用户认证、个人信息管理和学生数据管理功能。

## 🚀 功能特性

- **安全认证**：基于LDAP的用户认证系统
- **个人信息管理**：学生可以查看和修改个人信息
- **学生数据管理**：管理员可以管理所有学生信息
- **批量导入**：支持CSV/Excel格式的批量学生数据导入
- **现代化界面**：响应式Web界面，支持移动端
- **安全防护**：防止回退访问、密码验证、会话管理

## 📋 系统要求

- Ubuntu 20.04+ 或 CentOS 7+
- Python 3.8+
- OpenLDAP 2.4+
- Nginx (可选，用于域名访问)

## 🛠️ 安装部署

### 1. 克隆项目
```bash
git clone <项目地址>
cd StudentLdapSystem
```

### 2. 创建虚拟环境
```bash
# 使用conda
conda create -n ldap-env python=3.10
conda activate ldap-env

# 或使用venv
python3 -m venv ldap-env
source ldap-env/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 安装OpenLDAP服务器
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install slapd ldap-utils

# CentOS/RHEL
sudo yum install openldap-servers openldap-clients
```

### 5. 配置OpenLDAP
```bash
# 重新配置LDAP
sudo dpkg-reconfigure slapd

# 设置域名：szuldpa-edu.com
# 设置组织名：szuldpa-edu
# 设置管理员密码
```

### 6. 初始化LDAP数据库
```bash
# 创建基础结构
sudo ldapadd -x -D "cn=admin,dc=szuldpa-edu,dc=com" -W -f ldap_config.ldif

# 运行初始化脚本
chmod +x setup_ldap.sh
./setup_ldap.sh
```

### 7. 启动Web应用
```bash
python app.py
```

访问：`http://localhost:5000`

## 👥 测试账号

| 用户名 | 密码 | 姓名 | 邮箱 |
|--------|------|------|------|
| student001 | 123456 | 张三 | student001@szuldpa-edu.com |
| student002 | 123456 | 李四 | student002@szuldpa-edu.com |
| student003 | 123456 | 王五 | student003@szuldpa-edu.com |
| student004 | 123456 | 赵六 | student004@szuldpa-edu.com |
| student005 | 123456 | 钱七 | student005@szuldpa-edu.com |

```

## 🔧 配置说明

### LDAP配置
- **域名**：szuldpa-edu.com
- **基础DN**：dc=szuldpa-edu,dc=com
- **学生OU**：ou=students,dc=szuldpa-edu,dc=com
- **管理员DN**：cn=admin,dc=szuldpa-edu,dc=com

### Web应用配置
- **端口**：5000
- **调试模式**：开启
- **会话密钥**：your-secret-key-here (生产环境请修改)

## 🌐 远程访问配置

### 方法1：直接IP访问
```bash
# 访问地址
http://服务器IP:5000
```

### 方法2：域名访问（推荐）
1. **配置Nginx**：
```bash
sudo cp nginx_config.conf /etc/nginx/sites-available/ldap-system
sudo ln -s /etc/nginx/sites-available/ldap-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

2. **配置DNS**：
```bash
# 在客户端hosts文件中添加
服务器IP ldap.szuldpa-edu.com
```

3. **访问地址**：
```
http://ldap.szuldpa-edu.com
```

## 📊 数据管理

### 批量导入学生数据
```python
from student_db_manager import StudentLDAPManager

# 创建管理器实例
manager = StudentLDAPManager()

# 连接LDAP
if manager.connect():
    # 从CSV导入
    manager.import_students_from_csv('students_sample.csv')
    
    # 从Ex
    
    manager.import_students_from_excel('students.xlsx')
    
    # 断开连接
    manager.disconnect()
```

### 单个学生操作
```python
# 添加学生
manager.add_student('student006', '孙八', '孙', 'student006@szuldpa-edu.com', '123456', '计算机2021-3班')

# 查询学生
student = manager.search_student('student001')

# 列出所有学生
students = manager.list_students()
```

## 🔒 安全特性

- **密码验证**：支持Base64编码和明文密码
- **会话管理**：安全的用户会话控制
- **缓存控制**：防止敏感页面被缓存
- **回退防护**：防止用户通过回退按钮访问已登出页面
- **权限控制**：基于角色的访问控制

## 🐛 故障排除

### 常见问题

1. **LDAP连接失败**
   ```bash
   # 检查LDAP服务状态
   sudo systemctl status slapd
   
   # 重启LDAP服务
   sudo systemctl restart slapd
   ```

2. **密码验证失败**
   - 检查密码格式（Base64编码或明文）
   - 确认用户存在于LDAP中

3. **Web应用无法访问**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep 5000
   
   # 检查防火墙
   sudo ufw status
   ```

4. **域名无法访问**
   - 检查Nginx配置
   - 确认DNS设置
   - 检查hosts文件配置

## 📝 开发说明

### 添加新功能
1. 在 `app.py` 中添加新的路由
2. 在 `templates/` 中创建对应的HTML模板
3. 在 `static/` 中添加CSS/JS资源

### 修改LDAP结构
1. 更新 `ldap_config.ldif`
2. 修改 `student_db_manager.py` 中的相关方法
3. 重新初始化LDAP数据库

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📞 支持

如有问题，请通过以下方式联系：
- 提交Issue
- 发送邮件至：support@szuldpa-edu.com

---

**注意**：本系统仅用于学习和测试目的，生产环境使用请进行适当的安全加固。