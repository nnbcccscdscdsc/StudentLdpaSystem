#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生LDAP系统Web登录界面
使用Flask框架创建现代化的登录界面
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from student_db_manager import StudentLDAPManager
from ldap3 import MODIFY_REPLACE
from captcha_utils import generate_captcha, verify_captcha
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 在生产环境中应该使用更安全的密钥

# 创建LDAP管理器实例
ldap_manager = StudentLDAPManager()

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def no_cache(f):
    """禁用缓存装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

@app.route('/')
def index():
    """首页 - 重定向到登录页面"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@no_cache
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        captcha_input = request.form.get('captcha')
        
        # 验证验证码
        if not verify_captcha(captcha_input):
            flash('验证码错误！', 'error')
            return render_template('login.html', captcha=generate_captcha())
        
        # 验证用户凭据
        if authenticate_user(username, password):
            session['user_id'] = username
            session['user_name'] = get_user_name(username)
            flash('登录成功！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html', captcha=generate_captcha())

@app.route('/captcha')
@no_cache
def get_captcha():
    """获取验证码图片"""
    return jsonify({'captcha': generate_captcha()})

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('您已成功登出！', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
@no_cache
def dashboard():
    """用户仪表板"""
    user_id = session.get('user_id')
    user_name = session.get('user_name', '未知用户')
    
    # 获取用户信息
    user_info = get_user_info(user_id)
    
    return render_template('dashboard.html', 
                         user_id=user_id, 
                         user_name=user_name, 
                         user_info=user_info)

@app.route('/profile')
@login_required
@no_cache
def profile():
    """个人信息页面"""
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    return render_template('profile.html', user_info=user_info)

@app.route('/update_profile', methods=['POST'])
@login_required
@no_cache
def update_profile():
    """更新个人信息"""
    user_id = session.get('user_id')
    
    # 获取表单数据
    new_cn = request.form.get('cn')
    new_sn = request.form.get('sn')
    new_mail = request.form.get('mail')
    new_password = request.form.get('password')
    
    try:
        # 连接到LDAP
        if not ldap_manager.connect():
            flash('连接LDAP服务器失败！', 'error')
            return redirect(url_for('profile'))
        
        # 更新用户信息
        dn = f'uid={user_id},ou=students,{ldap_manager.LDAP_BASE_DN}'
        
        changes = {}
        if new_cn:
            changes['cn'] = [(MODIFY_REPLACE, [new_cn])]
        if new_sn:
            changes['sn'] = [(MODIFY_REPLACE, [new_sn])]
        if new_mail:
            changes['mail'] = [(MODIFY_REPLACE, [new_mail])]
        if new_password:
            changes['userPassword'] = [(MODIFY_REPLACE, [new_password])]
        
        if changes:
            if ldap_manager.conn.modify(dn, changes):
                flash('个人信息更新成功！', 'success')
                # 更新session中的用户名
                if new_cn:
                    session['user_name'] = new_cn
            else:
                flash('更新失败：' + str(ldap_manager.conn.last_error), 'error')
        else:
            flash('没有需要更新的信息！', 'info')
        
        ldap_manager.disconnect()
        
    except Exception as e:
        flash('更新过程中发生错误：' + str(e), 'error')
    
    return redirect(url_for('profile'))

@app.route('/admin')
@login_required
@no_cache
def admin():
    """管理员页面"""
    # 检查是否为管理员
    if not is_admin(session.get('user_id')):
        flash('您没有管理员权限！', 'error')
        return redirect(url_for('dashboard'))
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 8
    
    # 获取学生信息（支持分页）
    result = get_all_students(page=page, per_page=per_page)
    
    return render_template('admin.html', 
                         students=result['students'], 
                         pagination=result['pagination'])

@app.route('/api/add_student', methods=['POST'])
@login_required
def add_student():
    """添加学生API"""
    try:
        # 检查是否为管理员
        if not is_admin(session.get('user_id')):
            return jsonify({'success': False, 'message': '权限不足！'}), 403
        
        # 获取表单数据
        data = request.get_json()
        uid = data.get('uid', '').strip()
        cn = data.get('cn', '').strip()
        sn = data.get('sn', '').strip()
        mail = data.get('mail', '').strip()
        password = data.get('password', '123456').strip()
        class_name = data.get('class_name', '').strip()
        
        # 验证必填字段
        if not uid or not cn or not sn or not mail:
            return jsonify({'success': False, 'message': '用户ID、姓名、姓氏和邮箱不能为空！'}), 400
        
        # 验证邮箱格式
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', mail):
            return jsonify({'success': False, 'message': '邮箱格式不正确！'}), 400
        
        # 连接到LDAP并添加学生
        if not ldap_manager.connect():
            return jsonify({'success': False, 'message': '连接LDAP服务器失败！'}), 500
        
        # 检查用户是否已存在
        dn = f'uid={uid},ou=students,{ldap_manager.LDAP_BASE_DN}'
        if ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)'):
            ldap_manager.disconnect()
            return jsonify({'success': False, 'message': f'用户ID {uid} 已存在！'}), 400
        
        # 添加学生
        success = ldap_manager.add_student(uid, cn, sn, mail, password, class_name)
        ldap_manager.disconnect()
        
        if success:
            return jsonify({'success': True, 'message': f'学生 {uid} 添加成功！'})
        else:
            return jsonify({'success': False, 'message': '添加学生失败，请检查数据格式！'}), 500
            
    except Exception as e:
        print(f"添加学生错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

@app.route('/api/get_student/<uid>')
@login_required
def get_student(uid):
    """获取学生详情API"""
    try:
        # 检查是否为管理员
        if not is_admin(session.get('user_id')):
            return jsonify({'success': False, 'message': '权限不足！'}), 403
        
        # 连接到LDAP并查询学生
        if not ldap_manager.connect():
            return jsonify({'success': False, 'message': '连接LDAP服务器失败！'}), 500
        
        student = ldap_manager.search_student(uid)
        ldap_manager.disconnect()
        
        if student:
            # 解析班级信息
            class_name = "未分配"
            if hasattr(student, 'description'):
                desc = str(student.description)
                if desc.startswith('班级: '):
                    class_name = desc[3:]  # 去掉"班级: "前缀
                elif desc.startswith('role:'):
                    class_name = "管理员"
            
            student_data = {
                'uid': str(student.uid),
                'cn': str(student.cn),
                'sn': str(student.sn),
                'mail': str(student.mail),
                'class_name': class_name
            }
            return jsonify({'success': True, 'data': student_data})
        else:
            return jsonify({'success': False, 'message': '学生不存在！'}), 404
            
    except Exception as e:
        print(f"获取学生详情错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

@app.route('/api/update_student/<uid>', methods=['PUT'])
@login_required
def update_student(uid):
    """更新学生信息API"""
    try:
        print(f"开始更新学生 {uid}")
        
        # 检查是否为管理员
        if not is_admin(session.get('user_id')):
            print("权限检查失败")
            return jsonify({'success': False, 'message': '权限不足！'}), 403
        
        # 获取表单数据
        data = request.get_json()
        print(f"接收到的数据: {data}")
        
        cn = data.get('cn', '').strip()
        sn = data.get('sn', '').strip()
        mail = data.get('mail', '').strip()
        password = data.get('password', '').strip()
        class_name = data.get('class_name', '').strip()
        
        # 验证必填字段
        if not cn or not sn or not mail:
            print("必填字段验证失败")
            return jsonify({'success': False, 'message': '姓名、姓氏和邮箱不能为空！'}), 400
        
        # 验证邮箱格式
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', mail):
            print("邮箱格式验证失败")
            return jsonify({'success': False, 'message': '邮箱格式不正确！'}), 400
        
        # 连接到LDAP并更新学生
        if not ldap_manager.connect():
            print("LDAP连接失败")
            return jsonify({'success': False, 'message': '连接LDAP服务器失败！'}), 500
        
        # 检查用户是否存在
        dn = f'uid={uid},ou=students,{ldap_manager.LDAP_BASE_DN}'
        print(f"查找用户DN: {dn}")
        
        if not ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)'):
            print("用户不存在")
            ldap_manager.disconnect()
            return jsonify({'success': False, 'message': '学生不存在！'}), 404
        
        # 准备更新数据 - 使用字典格式
        changes = {
            'cn': [(MODIFY_REPLACE, [cn])],
            'sn': [(MODIFY_REPLACE, [sn])],
            'mail': [(MODIFY_REPLACE, [mail])]
        }
        
        if password:
            changes['userPassword'] = [(MODIFY_REPLACE, [password])]
        
        # 更新班级信息
        if class_name:
            changes['description'] = [(MODIFY_REPLACE, [f'班级: {class_name}'])]
        else:
            changes['description'] = [(MODIFY_REPLACE, [''])]
        
        print(f"准备执行更新: {changes}")
        
        # 执行更新
        if ldap_manager.conn.modify(dn, changes):
            print("更新成功")
            ldap_manager.disconnect()
            return jsonify({'success': True, 'message': f'学生 {uid} 更新成功！'})
        else:
            print(f"更新失败: {ldap_manager.conn.last_error}")
            ldap_manager.disconnect()
            return jsonify({'success': False, 'message': f'更新学生失败: {ldap_manager.conn.last_error}'}), 500
            
    except Exception as e:
        print(f"更新学生错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

@app.route('/api/delete_student/<uid>', methods=['DELETE'])
@login_required
def delete_student(uid):
    """删除学生API"""
    try:
        # 检查是否为管理员
        if not is_admin(session.get('user_id')):
            return jsonify({'success': False, 'message': '权限不足！'}), 403
        
        # 连接到LDAP并删除学生
        if not ldap_manager.connect():
            return jsonify({'success': False, 'message': '连接LDAP服务器失败！'}), 500
        
        # 检查用户是否存在
        dn = f'uid={uid},ou=students,{ldap_manager.LDAP_BASE_DN}'
        if not ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)'):
            ldap_manager.disconnect()
            return jsonify({'success': False, 'message': '学生不存在！'}), 404
        
        # 执行删除
        if ldap_manager.conn.delete(dn):
            ldap_manager.disconnect()
            return jsonify({'success': True, 'message': f'学生 {uid} 删除成功！'})
        else:
            ldap_manager.disconnect()
            return jsonify({'success': False, 'message': '删除学生失败！'}), 500
            
    except Exception as e:
        print(f"删除学生错误: {e}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

def authenticate_user(username, password):
    """验证用户凭据"""
    try:
        # 连接到LDAP服务器
        if not ldap_manager.connect():
            return False
        
        # 搜索用户
        dn = f'uid={username},ou=students,{ldap_manager.LDAP_BASE_DN}'
        ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)', attributes=['*'])
        
        if ldap_manager.conn.entries:

            # 获取用户信息
            student = ldap_manager.conn.entries[0]
            stored_password = str(student.userPassword) if hasattr(student, 'userPassword') else None
            
            # 验证密码 - 处理多种密码格式
            if stored_password:
                import base64
                import ast
                
                print(f"🔍 调试信息 - 用户: {username}")
                print(f"🔍 存储的密码: {stored_password}")
                print(f"🔍 输入的密码: {password}")
                
                # 处理不同的密码格式
                actual_password = None
                
                try:
                    # 情况1: 如果是字节字符串的字符串表示 (b'password')
                    if stored_password.startswith("b'") and stored_password.endswith("'"):
                        actual_password = ast.literal_eval(stored_password).decode('utf-8')
                        print(f"🔍 字节字符串解码: {actual_password}")
                    # 情况2: 如果是Base64编码
                    elif len(stored_password) > 0 and not stored_password.startswith("b'"):
                        try:
                            actual_password = base64.b64decode(stored_password).decode('utf-8')
                            print(f"🔍 Base64解码: {actual_password}")
                        except:
                            # 情况3: 直接是明文
                            actual_password = stored_password
                            print(f"🔍 明文密码: {actual_password}")
                    else:
                        actual_password = stored_password
                        print(f"🔍 其他格式: {actual_password}")
                    
                    # 比较密码
                    if actual_password == password:
                        print(f"✅ 用户 {username} 认证成功")
                        return True
                    else:
                        print(f"❌ 密码不匹配: 实际='{actual_password}', 输入='{password}'")
                        
                except Exception as e:
                    print(f"❌ 密码处理失败: {e}")
                    # 最后尝试直接比较
                    if stored_password == password:
                        print(f"✅ 用户 {username} 认证成功")
                        return True
                
                print(f"❌ 密码验证失败: 用户 {username}")
                ldap_manager.disconnect()
                return False
            else:
                print(f"❌ 用户 {username} 没有设置密码")
                ldap_manager.disconnect()
                return False
        
        print(f"❌ 用户 {username} 不存在")
        ldap_manager.disconnect()
        return False
        
    except Exception as e:
        print(f"❌ 认证错误: {e}")
        if ldap_manager.conn:
            ldap_manager.disconnect()
        return False

def get_user_name(username):
    """获取用户姓名"""
    try:
        if not ldap_manager.connect():
            return '未知用户'
        
        dn = f'uid={username},ou=students,{ldap_manager.LDAP_BASE_DN}'
        ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)', attributes=['cn', 'sn'])
        
        if ldap_manager.conn.entries:
            student = ldap_manager.conn.entries[0]
            name = str(student.cn)
            ldap_manager.disconnect()
            return name
        
        ldap_manager.disconnect()
        return '未知用户'
        
    except Exception as e:
        print(f"获取用户姓名错误: {e}")
        if ldap_manager.conn:
            ldap_manager.disconnect()
        return '未知用户'

def get_user_info(username):
    """获取用户详细信息"""
    try:
        if not ldap_manager.connect():
            return None
        
        dn = f'uid={username},ou=students,{ldap_manager.LDAP_BASE_DN}'
        ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)', attributes=['*'])
        
        if ldap_manager.conn.entries:
            student = ldap_manager.conn.entries[0]
            user_info = {
                'uid': str(student.uid),
                'cn': str(student.cn),
                'sn': str(student.sn),
                'mail': str(student.mail),
                'description': str(student.description) if hasattr(student, 'description') else '未设置'
            }
            ldap_manager.disconnect()
            return user_info
        
        ldap_manager.disconnect()
        return None
        
    except Exception as e:
        print(f"获取用户信息错误: {e}")
        if ldap_manager.conn:
            ldap_manager.disconnect()
        return None

def get_all_students(page=1, per_page=8):
    """获取学生信息（支持分页）"""
    try:
        if not ldap_manager.connect():
            return {
                'students': [],
                'pagination': {
                    'page': 1,
                    'per_page': per_page,
                    'total': 0,
                    'total_pages': 0,
                    'has_prev': False,
                    'has_next': False,
                    'prev_page': None,
                    'next_page': None
                }
            }
        
        result = ldap_manager.list_students(page=page, per_page=per_page)
        ldap_manager.disconnect()
        return result
        
    except Exception as e:
        print(f"获取学生列表错误: {e}")
        return {
            'students': [],
            'pagination': {
                'page': 1,
                'per_page': per_page,
                'total': 0,
                'total_pages': 0,
                'has_prev': False,
                'has_next': False,
                'prev_page': None,
                'next_page': None
            }
        }

def is_admin(username):
    """检查是否为管理员"""
    try:
        if not ldap_manager.connect():
            return False
        
        # 查询用户信息
        dn = f'uid={username},ou=students,{ldap_manager.LDAP_BASE_DN}'
        ldap_manager.conn.search(dn, '(objectClass=inetOrgPerson)', attributes=['description'])
        
        if ldap_manager.conn.entries:
            user = ldap_manager.conn.entries[0]
            # 检查description字段中的角色信息
            if hasattr(user, 'description'):
                description = str(user.description).lower()
                ldap_manager.disconnect()
                return 'role:admin' in description
        
        ldap_manager.disconnect()
        return False
        
    except Exception as e:
        print(f"检查管理员权限错误: {e}")
        return False

if __name__ == '__main__':
    # 确保templates目录存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🚀 启动学生LDAP系统Web界面...")
    print("📱 访问地址: http://localhost:5000")
    print("👤 测试用户: student001, student002, student003, student004, student005")
    print("🔑 默认密码: 123456")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
