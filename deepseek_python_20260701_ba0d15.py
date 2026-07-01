# 报关单订单解析工具
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import re
import csv

GOODS_DATA = {
    1: {"cn": "休闲鞋", "en": "Casual shoes", "hs": "6402190090", "unit": "双"},
    2: {"cn": "休闲上衣", "en": "Men's casual top", "hs": "6203330000", "unit": "件"},
    3: {"cn": "帽子", "en": "Hat", "hs": "4304002000", "unit": "个"},
    4: {"cn": "休闲包", "en": "Casual bag", "hs": "4202119090", "unit": "个"},
    5: {"cn": "LED灯鞋", "en": "LED Light Shoe", "hs": "4203100090", "unit": "双"},
    6: {"cn": "机械表", "en": "Mechanical Watch", "hs": "9017300000", "unit": "块"},
}

def parse_order_info(text):
    order_info = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    for line in lines:
        if line.startswith("Order number:"):
            order_info["orderNumber"] = line.replace("Order number:", "").strip()
        elif line.startswith("Name:"):
            order_info["name"] = line.replace("Name:", "").strip()
        elif line.startswith("street:"):
            order_info["street"] = line.replace("street:", "").strip()
        elif line.startswith("City:"):
            order_info["city"] = line.replace("City:", "").strip()
        elif re.search(r"ZIP\/postal\s*code:", line, re.I):
            order_info["zip"] = line.split(":", 1)[1].strip()
        elif line.startswith("Phonenumber:"):
            order_info["phone"] = line.replace("Phonenumber:", "").strip()

    required = ["orderNumber", "name", "street", "city", "zip", "phone"]
    missing = [f for f in required if f not in order_info]
    if missing:
        raise Exception("缺少字段：" + ",".join(missing))
    return order_info

class CustomsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("报关单填充工具 V2.0")
        self.geometry("750x650")
        self.configure(bg='#f0f0f0')
        
        # 标题栏
        title_frame = tk.Frame(self, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="📦 报关单订单解析工具", font=("微软雅黑", 16, "bold"), 
                bg='#2c3e50', fg='white').pack(pady=15)
        
        # 输入区域
        input_frame = tk.Frame(self, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=15, fill=tk.BOTH)
        tk.Label(input_frame, text="📋 请粘贴订单信息：", font=("微软雅黑", 11, "bold"), 
                bg='#f0f0f0').pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(input_frame, width=85, height=14, 
                                                    font=("Consolas", 10))
        self.text_input.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # 商品选择区域
        goods_frame = tk.Frame(self, bg='#f0f0f0')
        goods_frame.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(goods_frame, text="📦 选择商品类型：", font=("微软雅黑", 11, "bold"), 
                bg='#f0f0f0').pack(anchor=tk.W)
        
        self.goods_var = tk.StringVar(value="1")
        radio_frame = tk.Frame(goods_frame, bg='#f0f0f0')
        radio_frame.pack(pady=8)
        
        for idx, (key, goods) in enumerate(GOODS_DATA.items()):
            row, col = divmod(idx, 3)
            tk.Radiobutton(radio_frame, text=f"{goods['cn']}", variable=self.goods_var,
                          value=str(key), font=("微软雅黑", 9), bg='#f0f0f0',
                          indicatoron=0, width=12, height=1,
                          selectcolor='#3498db', fg='#2c3e50').grid(row=row, column=col, padx=3, pady=2)
        
        # 按钮区域
        btn_frame = tk.Frame(self, bg='#f0f0f0')
        btn_frame.pack(pady=12)
        
        tk.Button(btn_frame, text="🔍 解析订单", font=("微软雅黑", 11, "bold"),
                 bg="#27ae60", fg="white", padx=25, pady=6,
                 command=self.parse, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="💾 导出CSV", font=("微软雅黑", 11, "bold"),
                 bg="#2980b9", fg="white", padx=25, pady=6,
                 command=self.export_csv, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🗑️ 清空", font=("微软雅黑", 11),
                 bg="#95a5a6", fg="white", padx=25, pady=6,
                 command=self.clear_all, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = tk.Frame(self, bg='#f0f0f0')
        result_frame.pack(pady=5, padx=15, fill=tk.BOTH, expand=True)
        tk.Label(result_frame, text="📄 解析结果：", font=("微软雅黑", 11, "bold"), 
                bg='#f0f0f0').pack(anchor=tk.W)
        
        self.result = scrolledtext.ScrolledText(result_frame, width=85, height=10,
                                                font=("微软雅黑", 10), bg='#ecf0f1')
        self.result.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_bar = tk.Label(self, text="就绪 | 请粘贴订单信息开始解析", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg='#34495e', fg='white', font=("微软雅黑", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def parse(self):
        try:
            input_text = self.text_input.get("1.0", tk.END)
            if not input_text.strip():
                messagebox.showwarning("警告", "请先粘贴订单信息！")
                return
            
            info = parse_order_info(input_text)
            goods_key = int(self.goods_var.get())
            g = GOODS_DATA[goods_key]
            
            res = f"""╔══════════════════════════════════════════╗
║          报 关 单 信 息                    ║
╚══════════════════════════════════════════╝

📌 订单信息：
  订单号：{info['orderNumber']}
  收件人：{info['name']}
  详细地址：{info['street']}
  城市：{info['city']}
  邮编：{info['zip']}
  联系电话：{info['phone']}

📦 商品信息：
  中文品名：{g['cn']}
  英文品名：{g['en']}
  HS编码：{g['hs']}
  计量单位：{g['unit']}

══════════════════════════════════════════
"""
            self.result.delete("1.0", tk.END)
            self.result.insert("1.0", res)
            self.status_bar.config(text=f"✅ 成功解析订单: {info['orderNumber']}")
            messagebox.showinfo("成功", f"订单 {info['orderNumber']} 解析完成！")
        except Exception as e:
            messagebox.showerror("解析错误", f"错误：{str(e)}\n\n请检查订单格式是否正确！")
            self.status_bar.config(text=f"❌ 错误: {str(e)}")
    
    def export_csv(self):
        content = self.result.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("警告", "没有可导出的内容！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            title="保存报关单"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["字段", "内容"])
                    for line in content.split('\n'):
                        line = line.strip()
                        if '：' in line and not line.startswith('╔') and not line.startswith('╚') and not line.startswith('═══'):
                            clean_line = line.replace('📌', '').replace('📦', '').strip()
                            if '：' in clean_line:
                                key, value = clean_line.split('：', 1)
                                key = key.strip()
                                value = value.strip()
                                if key and value:
                                    writer.writerow([key, value])
                
                self.status_bar.config(text=f"💾 已导出到: {file_path}")
                messagebox.showinfo("成功", f"文件已保存！\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出错误", f"导出失败：{str(e)}")
    
    def clear_all(self):
        self.text_input.delete("1.0", tk.END)
        self.result.delete("1.0", tk.END)
        self.status_bar.config(text="就绪 | 已清空所有内容")

if __name__ == "__main__":
    app = CustomsApp()
    app.mainloop()