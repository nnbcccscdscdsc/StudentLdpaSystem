#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生LDAP数据管理系统
支持增删改查和批量导入功能

# 添加学生（按照LDAP标准）
manager.add_student('student001', '张三', '张', 'student001@szuldpa-edu.com', '123456', '计算机2021-1班')

# CSV文件格式
uid,cn,sn,mail,password,class_name
student001,张三,张,student001@szuldpa-edu.com,123456,计算机2021-1班
"""

import csv
import pandas as pd
import getpass
import hashlib
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SUBTREE
import os
import sys

class StudentLDAPManager:
    def __init__(self):
        # LDAP 配置信息
        self.LDAP_SERVER = 'ldap://localhost:389'
        self.LDAP_BASE_DN = 'dc=szuldpa-edu,dc=com'
        self.LDAP_ADMIN_DN = 'cn=admin,dc=szuldpa-edu,dc=com'
        self.LDAP_ADMIN_PASSWORD = None
        self.conn = None
        
    def connect(self):
        """连接到LDAP服务器"""
        try:
            # 如果没有设置密码，从环境变量或配置文件获取
            if not self.LDAP_ADMIN_PASSWORD:
                import os
                # 优先从环境变量获取
                self.LDAP_ADMIN_PASSWORD = os.getenv('LDAP_ADMIN_PASSWORD')
                
                # 如果环境变量也没有，尝试从配置文件读取
                if not self.LDAP_ADMIN_PASSWORD:
                    try:
                        with open('.ldap_password', 'r') as f:
                            self.LDAP_ADMIN_PASSWORD = f.read().strip()
                    except FileNotFoundError:
                        pass
                
                # 如果都没有，提示用户输入
                if not self.LDAP_ADMIN_PASSWORD:
                    self.LDAP_ADMIN_PASSWORD = getpass.getpass("请输入LDAP管理员密码: ")
            
            server = Server(self.LDAP_SERVER, get_info=ALL)
            self.conn = Connection(server, user=self.LDAP_ADMIN_DN, password=self.LDAP_ADMIN_PASSWORD)
            
            if not self.conn.bind():
                print("❌ 连接LDAP服务器失败:", self.conn.last_error)
                return False
            else:
                print("✅ 成功连接到LDAP服务器")
                return True
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return False
    
    def disconnect(self):
        """断开LDAP连接"""
        if self.conn:
            self.conn.unbind()
            print("🔌 已断开LDAP连接")

    def create_ou_structure(self):
        """创建组织单位结构"""
        try:
            # 创建学生OU
            students_ou = f'ou=students,{self.LDAP_BASE_DN}'
            if not self.conn.search(students_ou, '(objectClass=organizationalUnit)'):
                self.conn.add(students_ou, ['organizationalUnit'], {'ou': 'students', 'description': '学生信息组织单位'})
                print("✅ 创建学生OU成功")
            
            # 创建教师OU
            teachers_ou = f'ou=teachers,{self.LDAP_BASE_DN}'
            if not self.conn.search(teachers_ou, '(objectClass=organizationalUnit)'):
                self.conn.add(teachers_ou, ['organizationalUnit'], {'ou': 'teachers', 'description': '教师信息组织单位'})
                print("✅ 创建教师OU成功")
            
            # 创建班级OU
            classes_ou = f'ou=classes,{self.LDAP_BASE_DN}'
            if not self.conn.search(classes_ou, '(objectClass=organizationalUnit)'):
                self.conn.add(classes_ou, ['organizationalUnit'], {'ou': 'classes', 'description': '班级信息组织单位'})
                print("✅ 创建班级OU成功")
                
        except Exception as e:
            print(f"❌ 创建OU结构失败: {e}")

    def add_student(self, uid, cn, sn, mail, password='123456', class_name=None):
        """增加学生数据"""
        try:
            dn = f'uid={uid},ou=students,{self.LDAP_BASE_DN}'
            
            # 检查学生是否已存在
            if self.conn.search(dn, '(objectClass=inetOrgPerson)'):
                print(f"⚠️  学生 {uid} 已存在")
                return False
            
            attributes = {
                'objectClass': ['inetOrgPerson'],
                'uid': uid,
                'cn': cn,  # 通用名称
                'sn': sn,  # 姓氏
                'mail': mail,
                'userPassword': password
            }
            
            if class_name:
                attributes['description'] = f'班级: {class_name}'
            
            if self.conn.add(dn, attributes=attributes):
                print(f"✅ 学生 {uid} ({cn}) 添加成功")
                return True
            else:
                print(f"❌ 添加学生 {uid} 失败: {self.conn.last_error}")
                return False
                
        except Exception as e:
            print(f"❌ 添加学生错误: {e}")
            return False

    def delete_student(self, uid):
        """删除学生数据"""
        try:
            dn = f'uid={uid},ou=students,{self.LDAP_BASE_DN}'
            
            if self.conn.delete(dn):
                print(f"✅ 学生 {uid} 删除成功")
                return True
            else:
                print(f"❌ 删除学生 {uid} 失败: {self.conn.last_error}")
                return False
                
        except Exception as e:
            print(f"❌ 删除学生错误: {e}")
            return False

    def modify_student(self, uid, attribute, new_value):
        """修改学生数据"""
        try:
            dn = f'uid={uid},ou=students,{self.LDAP_BASE_DN}'
            changes = {attribute: [(MODIFY_REPLACE, [new_value])]}
            
            if self.conn.modify(dn, changes):
                print(f"✅ 学生 {uid} 的 {attribute} 更新成功")
                return True
            else:
                print(f"❌ 更新学生 {uid} 失败: {self.conn.last_error}")
                return False
                
        except Exception as e:
            print(f"❌ 修改学生错误: {e}")
            return False

    def search_student(self, uid):
        """查询单个学生数据"""
        try:
            dn = f'uid={uid},ou=students,{self.LDAP_BASE_DN}'
            self.conn.search(dn, '(objectClass=inetOrgPerson)', attributes=['*'])
            
            if self.conn.entries:
                student = self.conn.entries[0]
                print(f"📋 学生信息 - {uid}:")
                print(f"   姓名: {student.cn}")
                print(f"   姓氏: {student.sn}")
                print(f"   邮箱: {student.mail}")
                if hasattr(student, 'description'):
                    print(f"   班级: {student.description}")
                return student
            else:
                print(f"❌ 未找到学生 {uid}")
                return None
                
        except Exception as e:
            print(f"❌ 查询学生错误: {e}")
            return None

    def list_students(self, page=1, per_page=8):
        """列出学生（支持分页）"""
        try:
            self.conn.search(f'ou=students,{self.LDAP_BASE_DN}', '(objectClass=inetOrgPerson)', 
                           attributes=['uid', 'cn', 'sn', 'mail', 'description'])
            
            all_students = []
            for entry in self.conn.entries:
                # 解析班级信息
                class_name = "未分配"
                if hasattr(entry, 'description'):
                    desc = str(entry.description)
                    if desc.startswith('班级: '):
                        class_name = desc[3:]  # 去掉"班级: "前缀
                    elif desc.startswith('role:'):
                        class_name = "管理员"
                
                all_students.append({
                    'uid': str(entry.uid),
                    'cn': str(entry.cn),
                    'sn': str(entry.sn),
                    'mail': str(entry.mail),
                    'class_name': class_name
                })
            
            # 分页计算
            total = len(all_students)
            start = (page - 1) * per_page
            end = start + per_page
            students = all_students[start:end]
            
            # 分页信息
            total_pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            print(f"📊 共找到 {total} 名学生，第 {page}/{total_pages} 页")
            for student in students:
                print(f"   {student['uid']}: {student['cn']} ({student['class_name']})")
            
            return {
                'students': students,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_prev': has_prev,
                    'has_next': has_next,
                    'prev_page': page - 1 if has_prev else None,
                    'next_page': page + 1 if has_next else None
                }
            }
            
        except Exception as e:
            print(f"❌ 列出学生错误: {e}")
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

    def import_students_from_csv(self, csv_file):
        """批量导入学生数据（CSV文件）"""
        try:
            if not os.path.exists(csv_file):
                print(f"❌ 文件不存在: {csv_file}")
                return False
            
            students = pd.read_csv(csv_file)
            success_count = 0
            error_count = 0
            
            print(f"📁 开始导入CSV文件: {csv_file}")
            print(f"📊 共 {len(students)} 条记录")
            
            for index, row in students.iterrows():
                try:
                    uid = str(row['uid']).strip()
                    cn = str(row['cn']).strip()
                    sn = str(row['sn']).strip()
                    mail = str(row['mail']).strip()
                    password = str(row.get('password', '123456')).strip()
                    class_name = str(row.get('class_name', '')).strip() if 'class_name' in row else None
                    
                    if self.add_student(uid, cn, sn, mail, password, class_name):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"❌ 导入第 {index+1} 行数据失败: {e}")
                    error_count += 1
            
            print(f"✅ 导入完成: 成功 {success_count} 条, 失败 {error_count} 条")
            return True
            
        except Exception as e:
            print(f"❌ 导入CSV文件错误: {e}")
            return False

    def import_students_from_excel(self, excel_file):
        """批量导入学生数据（Excel文件）"""
        try:
            if not os.path.exists(excel_file):
                print(f"❌ 文件不存在: {excel_file}")
                return False
            
            students = pd.read_excel(excel_file)
            success_count = 0
            error_count = 0
            
            print(f"📁 开始导入Excel文件: {excel_file}")
            print(f"📊 共 {len(students)} 条记录")
            
            for index, row in students.iterrows():
                try:
                    uid = str(row['uid']).strip()
                    cn = str(row['cn']).strip()
                    sn = str(row['sn']).strip()
                    mail = str(row['mail']).strip()
                    password = str(row.get('password', '123456')).strip()
                    class_name = str(row.get('class_name', '')).strip() if 'class_name' in row else None
                    
                    if self.add_student(uid, cn, sn, mail, password, class_name):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"❌ 导入第 {index+1} 行数据失败: {e}")
                    error_count += 1
            
            print(f"✅ 导入完成: 成功 {success_count} 条, 失败 {error_count} 条")
            return True
            
        except Exception as e:
            print(f"❌ 导入Excel文件错误: {e}")
            return False


def main():
    """主函数 - 演示如何使用"""
    manager = StudentLDAPManager()
    
    # 连接LDAP服务器
    if not manager.connect():
        return
    
    # 创建OU结构
    manager.create_ou_structure()
    
    # 示例操作
    print("\n=== 学生数据管理演示 ===")
    
    # 添加学生
    manager.add_student('student001', '张三', '张', 'student001@szuldpa-edu.com', '123456', '计算机2021-1班')
    manager.add_student('student002', '李四', '李', 'student002@szuldpa-edu.com', '123456', '计算机2021-1班')
    
    # 查询学生
    manager.search_student('student001')
    
    # 列出所有学生
    manager.list_students()
    
    # 修改学生信息
    manager.modify_student('student001', 'mail', 'new_email@szuldpa-edu.com')
    
    # 断开连接
    manager.disconnect()


if __name__ == "__main__":
    main()
