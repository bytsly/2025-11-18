"""
国服ID申请拒签管理系统
主程序文件

Copyright (c) 2025 BH2VLF. All rights reserved.
"""
__version__ = "0.02"

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
import shutil
from PIL import Image, ImageTk
import base64
from io import BytesIO
import re


def increment_version(version_str):
    """递增版本号，每次增加0.01"""
    try:
        current_version = float(version_str)
        new_version = current_version + 0.01
        return f"{new_version:.2f}"
    except ValueError:
        return version_str


class RejectionManagementSystem:
    """拒签管理系统主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"国服ID申请拒签管理 v{__version__}")
        self.root.geometry("1400x700")
        
        # 数据存储
        self.data_file = "rejection_data.json"
        self.image_dir = "images"
        self.records = []
        
        # 创建图片目录
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        
        # 加载数据
        self.load_data()
        
        # 初始化UI
        self.setup_ui()
        
        # 显示现有数据
        self.refresh_table()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="国服ID申请拒签管理", 
            font=("Microsoft YaHei", 20, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=10)
        
        # 版本信息
        version_label = ttk.Label(
            main_frame, 
            text=f"版本: v{__version__}", 
            font=("Microsoft YaHei", 10)
        )
        version_label.grid(row=1, column=0, columnspan=4, pady=2)
        
        # 版权信息
        copyright_label = ttk.Label(
            main_frame, 
            text="Copyright © 2025 BH2VLF. All rights reserved.", 
            font=("Microsoft YaHei", 8, "italic")
        )
        copyright_label.grid(row=2, column=0, columnspan=4, pady=2)
        
        # 输入框架
        input_frame = ttk.LabelFrame(main_frame, text="新增记录", padding="10")
        input_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        # 呼号
        ttk.Label(input_frame, text="呼号:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.callsign_entry = ttk.Entry(input_frame, width=20)
        self.callsign_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 申请时间
        ttk.Label(input_frame, text="申请时间:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.datetime_entry = ttk.Entry(input_frame, width=20)
        self.datetime_entry.grid(row=0, column=3, padx=5, pady=5)
        self.datetime_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # 执照照片
        ttk.Label(input_frame, text="执照照片:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.license_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.license_path, width=30, state="readonly").grid(
            row=1, column=1, columnspan=2, padx=5, pady=5
        )
        ttk.Button(input_frame, text="上传", command=lambda: self.upload_image("license")).grid(
            row=1, column=3, padx=5, pady=5
        )
        
        # 操作证照片
        ttk.Label(input_frame, text="操作证照片:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.operator_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.operator_path, width=30, state="readonly").grid(
            row=2, column=1, columnspan=2, padx=5, pady=5
        )
        ttk.Button(input_frame, text="上传", command=lambda: self.upload_image("operator")).grid(
            row=2, column=3, padx=5, pady=5
        )
        
        # 申请截图
        ttk.Label(input_frame, text="申请截图:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.screenshot_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.screenshot_path, width=30, state="readonly").grid(
            row=3, column=1, columnspan=2, padx=5, pady=5
        )
        ttk.Button(input_frame, text="上传", command=lambda: self.upload_image("screenshot")).grid(
            row=3, column=3, padx=5, pady=5
        )
        
        # 拒签原因
        ttk.Label(input_frame, text="拒签原因:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.reason_text = tk.Text(input_frame, width=50, height=4)
        self.reason_text.grid(row=4, column=1, columnspan=3, padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="添加记录", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空输入", command=self.clear_inputs).pack(side=tk.LEFT, padx=5)
        
        # 表格框架
        table_frame = ttk.LabelFrame(main_frame, text="拒签记录列表", padding="10")
        table_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 创建Treeview
        columns = ("呼号", "申请时间", "执照照片", "操作证照片", "申请截图", "拒签原因")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", height=15)
        
        # 设置列
        self.tree.column("#0", width=50, anchor=tk.CENTER)
        self.tree.heading("#0", text="序号")
        
        for col in columns:
            if col in ["呼号", "申请时间"]:
                self.tree.column(col, width=120, anchor=tk.CENTER)
            elif col in ["执照照片", "操作证照片", "申请截图"]:
                self.tree.column(col, width=100, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=250, anchor=tk.W)
            self.tree.heading(col, text=col)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 操作按钮
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(action_frame, text="查看图片", command=self.view_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="删除记录", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="刷新列表", command=self.refresh_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="导出数据", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="导入数据", command=self.import_data).pack(side=tk.LEFT, padx=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def upload_image(self, image_type):
        """上传图片"""
        callsign = self.callsign_entry.get().strip()
        if not callsign:
            messagebox.showwarning("警告", "请先填写呼号!")
            return
        
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"), ("所有文件", "*.*")]
        )
        
        if file_path:
            # 获取文件扩展名
            ext = os.path.splitext(file_path)[1]
            # 创建新文件名 (呼号_类型_时间戳.扩展名)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{callsign}_{image_type}_{timestamp}{ext}"
            new_path = os.path.join(self.image_dir, new_filename)
            
            # 复制文件
            shutil.copy2(file_path, new_path)
            
            # 更新对应的路径变量
            if image_type == "license":
                self.license_path.set(new_path)
            elif image_type == "operator":
                self.operator_path.set(new_path)
            elif image_type == "screenshot":
                self.screenshot_path.set(new_path)
            
            messagebox.showinfo("成功", f"{image_type}照片上传成功!")
    
    def add_record(self):
        """添加记录"""
        callsign = self.callsign_entry.get().strip()
        apply_time = self.datetime_entry.get().strip()
        license_img = self.license_path.get()
        operator_img = self.operator_path.get()
        screenshot_img = self.screenshot_path.get()
        reason = self.reason_text.get("1.0", tk.END).strip()
        
        # 验证必填项
        if not callsign:
            messagebox.showwarning("警告", "呼号不能为空!")
            return
        
        if not apply_time:
            messagebox.showwarning("警告", "申请时间不能为空!")
            return
        
        # 创建记录
        record = {
            "callsign": callsign,
            "apply_time": apply_time,
            "license_image": license_img,
            "operator_image": operator_img,
            "screenshot_image": screenshot_img,
            "rejection_reason": reason,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.records.append(record)
        self.save_data()
        self.refresh_table()
        self.clear_inputs()
        
        messagebox.showinfo("成功", "记录添加成功!")
    
    def clear_inputs(self):
        """清空输入框"""
        self.callsign_entry.delete(0, tk.END)
        self.datetime_entry.delete(0, tk.END)
        self.datetime_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.license_path.set("")
        self.operator_path.set("")
        self.screenshot_path.set("")
        self.reason_text.delete("1.0", tk.END)
    
    def refresh_table(self):
        """刷新表格"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for idx, record in enumerate(self.records, 1):
            license_status = "✓" if record.get("license_image") else "✗"
            operator_status = "✓" if record.get("operator_image") else "✗"
            screenshot_status = "✓" if record.get("screenshot_image") else "✗"
            
            self.tree.insert(
                "", 
                tk.END, 
                text=str(idx),
                values=(
                    record["callsign"],
                    record["apply_time"],
                    license_status,
                    operator_status,
                    screenshot_status,
                    record["rejection_reason"][:50] + "..." if len(record["rejection_reason"]) > 50 else record["rejection_reason"]
                )
            )
    
    def view_images(self):
        """查看图片"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一条记录!")
            return
        
        # 获取选中项的索引
        item = selected[0]
        index = int(self.tree.item(item, "text")) - 1
        record = self.records[index]
        
        # 创建图片查看窗口
        view_window = tk.Toplevel(self.root)
        view_window.title(f"呼号: {record['callsign']} - 图片查看")
        view_window.geometry("800x600")
        
        # 主框架
        main_frame = ttk.Frame(view_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部框架 - 倒品字形上面两个图片(执照和操作证)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左侧 - 执照照片
        left_frame = ttk.LabelFrame(top_frame, text="执照照片", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        license_img_path = record.get("license_image")
        if license_img_path and os.path.exists(license_img_path):
            try:
                img = Image.open(license_img_path)
                img.thumbnail((360, 250))
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(left_frame, image=photo)
                img_label.image = photo
                img_label.pack()
            except Exception as e:
                ttk.Label(left_frame, text=f"无法加载图片\n{str(e)}").pack()
        else:
            ttk.Label(left_frame, text="未上传图片", font=("Microsoft YaHei", 10)).pack(pady=50)
        
        # 右侧 - 操作证照片
        right_frame = ttk.LabelFrame(top_frame, text="操作证照片", padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        operator_img_path = record.get("operator_image")
        if operator_img_path and os.path.exists(operator_img_path):
            try:
                img = Image.open(operator_img_path)
                img.thumbnail((360, 250))
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(right_frame, image=photo)
                img_label.image = photo
                img_label.pack()
            except Exception as e:
                ttk.Label(right_frame, text=f"无法加载图片\n{str(e)}").pack()
        else:
            ttk.Label(right_frame, text="未上传图片", font=("Microsoft YaHei", 10)).pack(pady=50)
        
        # 下部框架 - 倒品字形下面的长条(申请截图)
        bottom_frame = ttk.LabelFrame(main_frame, text="申请截图", padding="5")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        screenshot_img_path = record.get("screenshot_image")
        if screenshot_img_path and os.path.exists(screenshot_img_path):
            try:
                img = Image.open(screenshot_img_path)
                img.thumbnail((760, 250))
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(bottom_frame, image=photo)
                img_label.image = photo
                img_label.pack()
            except Exception as e:
                ttk.Label(bottom_frame, text=f"无法加载图片\n{str(e)}").pack()
        else:
            ttk.Label(bottom_frame, text="未上传图片", font=("Microsoft YaHei", 10)).pack(pady=50)
    
    def delete_record(self):
        """删除记录"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一条记录!")
            return
        
        if messagebox.askyesno("确认", "确定要删除这条记录吗?"):
            item = selected[0]
            index = int(self.tree.item(item, "text")) - 1
            
            # 删除关联的图片文件
            record = self.records[index]
            for img_key in ["license_image", "operator_image", "screenshot_image"]:
                img_path = record.get(img_key)
                if img_path and os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except Exception as e:
                        print(f"删除图片失败: {e}")
            
            # 删除记录
            del self.records[index]
            self.save_data()
            self.refresh_table()
            
            messagebox.showinfo("成功", "记录删除成功!")
    
    def export_data(self):
        """导出数据"""
        if not self.records:
            messagebox.showwarning("警告", "没有数据可以导出!")
            return
        
        # 选择导出文件路径
        export_path = filedialog.asksaveasfilename(
            title="导出数据",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not export_path:
            return
        
        try:
            # 导出数据
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            
            # 提示用户是否也要复制图片目录
            if os.path.exists(self.image_dir) and os.listdir(self.image_dir):
                if messagebox.askyesno("导出成功", f"数据已导出到: {export_path}\n\n是否也导出图片目录?"):
                    # 选择图片目录导出位置
                    export_images_dir = filedialog.askdirectory(title="选择图片目录导出位置")
                    if export_images_dir:
                        # 创建目标目录
                        target_images_dir = os.path.join(export_images_dir, "images")
                        if os.path.exists(target_images_dir):
                            messagebox.showwarning("警告", f"目标目录 {target_images_dir} 已存在!")
                        else:
                            # 复制整个图片目录
                            shutil.copytree(self.image_dir, target_images_dir)
                            messagebox.showinfo("导出成功", f"数据已导出到: {export_path}\n图片已导出到: {target_images_dir}")
                    else:
                        messagebox.showinfo("导出成功", f"数据已导出到: {export_path}")
            else:
                messagebox.showinfo("导出成功", f"数据已导出到: {export_path}")
                
        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时发生错误:\n{str(e)}")
    
    def import_data(self):
        """导入数据"""
        # 选择要导入的数据文件
        import_path = filedialog.askopenfilename(
            title="选择要导入的数据文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not import_path:
            return
        
        try:
            # 读取导入的数据
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_records = json.load(f)
            
            # 验证数据格式
            if not isinstance(imported_records, list):
                messagebox.showerror("导入失败", "数据格式不正确!")
                return
            
            # 询问用户是否导入图片目录
            import_images = False
            source_images_dir = os.path.join(os.path.dirname(import_path), "images")
            if os.path.exists(source_images_dir) and os.listdir(source_images_dir):
                import_images = messagebox.askyesno("导入数据", "检测到图片目录，是否一起导入?")
            
            # 备份当前数据
            if self.records:
                backup_path = f"rejection_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(self.records, f, ensure_ascii=False, indent=2)
                
                if messagebox.askyesno("数据备份", f"当前数据已备份到: {backup_path}\n\n是否继续导入新数据?") == False:
                    return
            
            # 导入数据
            self.records = imported_records
            self.save_data()
            
            # 导入图片目录
            if import_images:
                if os.path.exists(self.image_dir):
                    # 删除现有图片目录
                    shutil.rmtree(self.image_dir)
                
                # 复制导入的图片目录
                shutil.copytree(source_images_dir, self.image_dir)
            
            # 刷新显示
            self.refresh_table()
            messagebox.showinfo("导入成功", f"成功导入 {len(imported_records)} 条记录!")
            
        except Exception as e:
            messagebox.showerror("导入失败", f"导入数据时发生错误:\n{str(e)}")
    
    def save_data(self):
        """保存数据到JSON文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """从JSON文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.records = []
        else:
            self.records = []


def main():
    """主函数"""
    root = tk.Tk()
    app = RejectionManagementSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
