import streamlit as st
import random
import time
from typing import Dict, Any

# =================================================================
# CSS Injection for Right-to-Left (RTL) Layout (راست چین سازی)
# =================================================================
def set_rtl_css():
    """تزریق CSS برای راست چین کردن تمامی عناصر متنی و دکمه ها"""
    st.markdown(
        """
        <style>
        /* تنظیم عمومی جهت متن برای کل بدنه صفحه */
        body {
            direction: rtl;
            unicode-bidi: embed;
        }
        /* تنظیم جهت متن برای تمامی ورودی ها، عنوان ها و دکمه ها */
        div, p, label, button, .stMarkdown, .stText, .stButton {
            direction: rtl;
            text-align: right;
        }
        /* تنظیم جدول ها و ستون های KPI */
        .stMetric, .stProgress, .stHeader, .stSubheader, .stAlert, .stWarning {
            direction: rtl;
            text-align: right;
        }
        /* اصلاح تراز برای input ها و Log box */
        input[type="text"], textarea, .stCodeEditor {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =================================================================
# ۱. کلاس اصلی وضعیت پروژه (Project State Variables) - منطق موتور
# =================================================================

class NiavaranProject:
    def __init__(self):
        # STC Initial Targets (اهداف اولیه)
        self.scope_target = 18  # 18 Phases/Months
        self.time_target = 18   # Months
        self.budget_target = 120_000_000_000  # 120 Billion Tomans

        # Current State (وضعیت فعلی)
        self.current_month = 1
        self.budget = self.budget_target
        self.time_remaining = self.time_target
        self.scope_progress = 0  # Phase Index
        
        # Extended Variables (پارامترهای کلیدی)
        self.quality = 90.0  # %
        self.safety = 90.0   # %
        self.client_satisfaction = 80.0  # %
        self.current_cost_of_risk = 0.0 # Accumulated cost from random events

        # Parameters (پارامترهای تأثیرگذار)
        self.base_monthly_cost = 6_000_000_000 # 6 Billion Toman
        self.morale = 80.0 # Hidden Morale 
        
        # Log for history (برای نمایش تاریخچه تصمیمات)
        self.log = []

    def update_status(self, cost_change, time_change, quality_change, safety_change, client_change, morale_change, extra_scope_cost=0):
        """اعمال تاثیر تصمیم کاربر بر وضعیت پروژه"""
        # Note: This function definition is slightly redundant due to apply_decision in GameEngine, 
        # but kept for consistency with the provided structure.
        
        self.budget -= (cost_change + extra_scope_cost)
        self.time_remaining -= time_change 
        
        self.quality = max(70, min(100, self.quality + quality_change))
        self.safety = max(70, min(100, self.safety + safety_change))
        self.client_satisfaction = max(70, min(100, self.client_satisfaction + client_change))
        self.morale = max(50, min(100, self.morale + morale_change))
        
        # Natural Burnout / Quality Pressure (Morale & Quality erode slightly)
        self.morale = max(50, self.morale - 2.0)
        self.quality = max(70, self.quality - 0.5)

class GameEngine:
    def __init__(self, project: NiavaranProject):
        self.project = project
        self.phases = [
            "تجهیز کارگاه و انتخاب پیمانکار", "گودبرداری و پایداری", "اجرای فونداسیون", "اسکلت: طبقات ۱-۲",
            "اسکلت: طبقات ۳-۴ (تأسیسات اولیه)", "اسکلت: طبقات ۵-۶ (احتمال برف)", "اسکلت: طبقات ۷-۸", 
            "سقف و پنت‌هاوس", "دیوارچینی و سفت‌کاری", "تأسیسات مکانیکی (خرید چیلر/پکیج)",
            "تأسیسات الکتریکی (تابلوبرق/کابل)", "کنترل کیفیت سفت‌کاری", "نازک‌کاری ۱ (نورپردازی/کناف)", 
            "نازک‌کاری ۲ (کابینت/کف‌سازی)", "نازک‌کاری ۳ (سرویس بهداشتی)", "محوطه‌سازی و فضای سبز",
            "تست و راه‌اندازی تأسیسات (چیلر/آب)", "تحویل نهایی و رفع نقص‌ها"
        ]
        self.random_events = self._setup_events()

    def _setup_events(self) -> Dict[str, Any]:
        """تعریف ریسک‌ها و رویدادهای تصادفی"""
        return {
            "R1": {"name": "افزایش ناگهانی قیمت آهن", "prob": 0.40, "month": [2, 3, 4], "impact_cost": 15_000_000_000},
            "R2": {"name": "شکایت همسایه‌ها", "prob": 0.25, "month": [2, 3], "impact_time": 0.5, "impact_cost": 500_000_000},
            "R3": {"name": "بارندگی/برف سنگین", "prob": 0.30, "month": [5, 6, 7, 8], "impact_time": 0.75},
            "R4": {"name": "تأخیر در تحویل سنگ نما", "prob": 0.35, "month": [7, 8], "impact_time": 1},
            "R5": {"name": "خرابی پمپ بتن", "prob": 0.20, "month": [3, 4], "impact_time": 0.3},
            "R7": {"name": "حادثه کارگاهی (HSE)", "prob": 0.15, "month": list(range(1, 18)), "impact_time": 0.25, "impact_safety": -5, "impact_morale": -10},
        }

    def apply_decision(self, cost_change, time_change, quality_change, safety_change, client_change, morale_change, extra_scope_cost=0):
        """اعمال تاثیر تصمیم کاربر بر وضعیت پروژه"""
        p = self.project
        
        # 1. Update STC based on decision
        p.budget -= cost_change + extra_scope_cost
        p.time_remaining -= time_change 
        
        # 2. Update Extended Variables
        p.quality = max(70, min(100, p.quality + quality_change))
        p.safety = max(70, min(100, p.safety + safety_change))
        p.client_satisfaction = max(70, min(100, p.client_satisfaction + client_change))
        p.morale = max(50, min(100, p.morale + morale_change))
        
        # 3. Natural Burnout / Quality Pressure (Morale & Quality erode slightly)
        p.morale = max(50, p.morale - 2.0)
        p.quality = max(70, p.quality - 0.5)

    def run_monthly_cycle(self):
        """اجرای محاسبات پایه برای هر ماه (یک نوبت)"""
        p = self.project
        
        if p.scope_progress >= p.scope_target:
            return # Project finished
        
        # Check for Game Over condition based on budget before proceeding
        if p.budget <= -20_000_000_000:
            p.log.append("🛑 **پایان بازی:** بودجه به شدت منفی شده و پروژه به حالت توقف اجباری درآمده است.")
            st.session_state.game_over = True
            return

        p.log.append(f"--- 🏗️ فاز {p.current_month}: {self.phases[p.scope_progress]} ---")
        
        # 1. Base Cost (I: Weekly Cost)
        p.budget -= p.base_monthly_cost
        
        # 2. Scope Progress (H: Scope Completed)
        # Morale Factor affects Scope Productivity/Time
        productivity_factor = 1 + ((p.morale - 80) / 100) # Morale > 80% is positive factor
        
        # Time and Scope logic: We assume 1 Phase is completed per month unless delayed
        time_impact = 1 / productivity_factor 
        
        if time_impact <= 1.2: # Successful execution (Max 20% delay tolerated by base productivity)
            p.scope_progress += 1
            p.time_remaining -= 1
            p.log.append(f"   [گزارش ماه]: فاز '{self.phases[p.scope_progress-1]}' در موعد مقرر تکمیل شد.")
        else: # Slow execution due to low morale/quality
            p.time_remaining -= 1 # Time passes
            # Check if scope progress is still within bounds before logging
            if p.scope_progress < len(self.phases):
                p.log.append(f"   [گزارش ماه]: ⚠️ تأخیر در اجرای فاز '{self.phases[p.scope_progress]}'. (Morale Effect)")
            else:
                 p.log.append("   [گزارش ماه]: ⚠️ تأخیر در اجرای آخرین فاز.")
            
        # 3. Check and apply Random Events
        self._check_random_events()

        p.current_month += 1

    def _check_random_events(self):
        """بررسی و اعمال ریسک‌ها در ماه جاری"""
        p = self.project
        applied_risk = False
        
        for key, event in self.random_events.items():
            if p.current_month in event.get("month", range(1, 18)) and random.random() < event["prob"]:
                
                p.log.append(f"🚨 **رویداد ریسکی فعال شد:** {event['name']}")
                
                # Apply Impacts
                if 'impact_cost' in event:
                    p.budget -= event['impact_cost']
                    p.current_cost_of_risk += event['impact_cost']
                    p.log.append(f"   [هزینه]: - {event['impact_cost'] / 1_000_000_000:.1f} میلیارد تومان")
                
                if 'impact_time' in event:
                    delay = event['impact_time']
                    p.time_remaining -= delay
                    p.log.append(f"   [زمان]: + {delay * 4:.1f} هفته تأخیر")
                    
                if 'impact_safety' in event:
                    p.safety = max(50, p.safety + event['impact_safety'])
                
                if 'impact_morale' in event:
                    p.morale = max(50, p.morale + event['impact_morale'])
                    
                applied_risk = True
        
        if not applied_risk:
            p.log.append("   [ریسک]: در این ماه رویداد تصادفی مهمی رخ نداد.")

def get_decision_options(month):
    """تعریف گزینه ها برای ماه های کلیدی"""
    if month == 1:
        return {
            'a': {'desc': "الف: پیمانکار ارزان (ریسک بالا)", 'cost': -5_000_000_000, 'quality': -5, 'safety': -5, 'morale': 0, 'client': 0, 'time': 0},
            'b': {'desc': "ب: پیمانکار با کیفیت متوسط (استاندارد)", 'cost': 0, 'quality': 0, 'safety': 0, 'morale': 0, 'client': 0, 'time': 0},
            'c': {'desc': "ج: پیمانکار لوکس و گران (کیفیت تضمینی)", 'cost': 5_000_000_000, 'quality': 5, 'safety': 5, 'morale': 5, 'client': 5, 'time': -0.1},
        }
        
    elif month == 7:
        return {
            'a': {'desc': "الف: سنگ وارداتی کیفیت بالا (گران)", 'cost': -8_000_000_000, 'quality': 10, 'client': 10, 'safety': 0, 'morale': 0, 'time': 0.2}, 
            'b': {'desc': "ب: سنگ ممتاز داخلی (استاندارد نیاوران)", 'cost': -3_000_000_000, 'quality': 5, 'client': 5, 'safety': 0, 'morale': 0, 'time': 0},
            'c': {'desc': "ج: سنگ تراورتن ارزان‌تر (صرفه جویی)", 'cost': 0, 'quality': -10, 'client': -10, 'safety': 0, 'morale': -5, 'time': 0},
        }
        
    elif month == 9:
        if random.random() < 0.3:
            st.warning("🚨 کارفرما تغییرات بزرگی را در پنت‌هاوس درخواست کرده است: هزینه +15 میلیارد، زمان +1.5 ماه.")
            return {
                'a': {'desc': "الف: پذیرش کامل تغییرات (حفظ رضایت)", 'cost': -15_000_000_000, 'time': 1.5, 'client': 15, 'quality': 5, 'safety': 0, 'morale': 10},
                'b': {'desc': "ب: مذاکره برای نسخه ساده‌تر", 'cost': -8_000_000_000, 'time': 0.5, 'client': 5, 'quality': 0, 'safety': 0, 'morale': 0},
                'c': {'desc': "ج: رد قاطع تغییرات", 'cost': 0, 'time': 0, 'client': -15, 'quality': 0, 'safety': 0, 'morale': -5},
            }
        else:
            return {
                'a': {'desc': "الف: جبران تأخیر با اضافه‌کاری (Crashing)", 'cost': -4_000_000_000, 'time': -0.25, 'client': 5, 'safety': -5, 'morale': -10, 'quality': -5},
                'b': {'desc': "ب: استفاده از مصالح ارزان‌تر موقت برای تسریع", 'cost': 0, 'time': -0.5, 'client': 0, 'safety': 0, 'morale': -5, 'quality': -10},
                'c': {'desc': "ج: حفظ کیفیت و پذیرش تأخیر", 'cost': 0, 'time': 0, 'client': 0, 'safety': 0, 'morale': 5, 'quality': 5},
            }
    else:
        return {
            'a': {'desc': "الف: کاهش هزینه با استفاده از مصالح داخلی ارزان‌تر", 'cost': 2_000_000_000, 'quality': -5, 'safety': -2, 'morale': -5, 'client': -5, 'time': 0},
            'b': {'desc': "ب: سرمایه‌گذاری در ایمنی و آموزش HSE", 'cost': -1_000_000_000, 'quality': 0, 'safety': 5, 'morale': 5, 'client': 0, 'time': 0},
            'c': {'desc': "ج: اجرای استاندارد (Default)", 'cost': 0, 'quality': 0, 'safety': 0, 'morale': 0, 'client': 0, 'time': 0},
        }

# =================================================================
# ۲. توابع رندرینگ Streamlit (رابط کاربری)
# =================================================================

def display_dashboard(project):
    """نمایش وضعیت پروژه در داشبورد گرافیکی"""
    st.header(f"📈 وضعیت پروژه در پایان ماه {project.current_month-1}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 بودجه باقی‌مانده (میلیارد تومان)", f"{project.budget / 1_000_000_000:,.1f}", "تومان")
    col2.metric("⏳ زمان باقی‌مانده (ماه)", f"{project.time_remaining:.1f}", "ماه")
    col3.metric("🛠️ پیشرفت (فاز)", f"{project.scope_progress} از {project.scope_target}", "فاز")

    st.subheader("پارامترهای کلیدی (کیفیت، ایمنی، رضایت)")
    
    col_ext1, col_ext2, col_ext3, col_ext4 = st.columns(4)
    col_ext1.metric("✅ کیفیت ساخت", f"{project.quality:.1f}%")
    col_ext2.metric("👷 ایمنی", f"{project.safety:.1f}%")
    col_ext3.metric("😊 رضایت کارفرما", f"{project.client_satisfaction:.1f}%")
    col_ext4.metric("❤️ روحیه تیم", f"{project.morale:.1f}%")

def display_final_result(project):
    """محاسبه و نمایش نتیجه نهایی بازی"""
    final_time = project.current_month - 1
    final_cost = project.budget_target - project.budget
    
    # Calculation of Final KPI Score (Weighted Average) - منطق از پاسخ قبلی
    time_score = max(0, 100 * (1 - (max(0, final_time - project.time_target) / project.time_target)))
    cost_score = max(0, 100 * (1 - (max(0, final_cost - project.budget_target) / project.budget_target) * 0.5))
    quality_score = project.quality
    safety_score = project.safety
    client_score = project.client_satisfaction

    final_kpi = (time_score * 0.3) + (cost_score * 0.3) + (quality_score * 0.2) + (safety_score * 0.1) + (client_score * 0.1)

    st.balloons()
    st.title("🎉 پروژه به پایان رسید!")
    st.subheader(f"امتیاز کل نهایی: **{final_kpi:.1f}**")
    
    st.write(f"زمان نهایی: {final_time} ماه | هزینه نهایی: {final_cost / 1_000_000_000:,.1f} میلیارد تومان")
    
    # Display Log
    st.markdown("### تاریخچه رویدادها")
    for entry in project.log:
        # Use st.info/st.error for key events to make them stand out
        if "رویداد ریسکی فعال شد" in entry:
            st.error(entry, icon="🚨")
        elif "تأخیر در اجرای فاز" in entry:
            st.warning(entry, icon="⚠️")
        elif entry.startswith("--- 🏗️"):
            st.info(entry)
        else:
            st.write(entry)
        
def handle_month_run():
    """هندلر دکمه 'اجرای ماه'"""
    if 'project' not in st.session_state:
        st.session_state.project = NiavaranProject()
    
    project = st.session_state.project
    engine = GameEngine(project)
    
    # 1. اجرای ماه قبل (اگر تصمیمی گرفته شده باشد)
    engine.run_monthly_cycle()
    
    # 2. بررسی اتمام بازی
    # Check budget again, as it might have dropped below the threshold during run_monthly_cycle
    if project.scope_progress >= project.scope_target or project.time_remaining <= 0 or project.budget <= -20_000_000_000:
        st.session_state.game_over = True
        return

def handle_decision_click(option_key):
    """هندلر کلیک بر روی گزینه تصمیم"""
    if 'project' not in st.session_state:
        return
        
    project = st.session_state.project
    engine = GameEngine(project)
    
    options = get_decision_options(project.current_month)
    # Check if option_key is valid
    if option_key not in options:
        project.log.append(f"خطا: گزینه '{option_key}' برای ماه {project.current_month} معتبر نیست.")
        st.rerun()
        return

    selected_option = options[option_key]

    # اعمال تغییرات تصمیم بر وضعیت پروژه
    engine.apply_decision(
        cost_change=selected_option.get('cost', 0),
        time_change=selected_option.get('time', 0),
        quality_change=selected_option.get('quality', 0),
        safety_change=selected_option.get('safety', 0),
        client_change=selected_option.get('client', 0),
        morale_change=selected_option.get('morale', 0)
    )

    # ثبت تصمیم در لاگ
    cost_disp = f"{(selected_option.get('cost', 0) / 1_000_000_000):.1f}B"
    time_disp = f"{(selected_option.get('time', 0)):.1f}M"
    
    project.log.append(
        f"✅ **تصمیم شما در ماه {project.current_month}:** {selected_option['desc']} | "
        f"تأثیر (هزینه: {cost_disp}, زمان: {time_disp}, روحیه: {selected_option.get('morale', 0)})"
    )
    
    # بعد از تصمیم، ماه جدید اجرا می‌شود.
    handle_month_run()
    st.rerun() # استفاده از st.rerun() بجای experimental_rerun

# =================================================================
# ۳. رانر اصلی اپلیکیشن Streamlit
# =================================================================
def main():
    st.set_page_config(layout="wide")
    
    # فراخوانی تابع راست چین سازی
    set_rtl_css() 
    
    st.title("🏗️ شبیه‌ساز ساخت‌وساز نیاوران (MVP)")
    st.markdown("---")

    # Initialize state
    if 'project' not in st.session_state:
        st.session_state.project = NiavaranProject()
        st.session_state.game_over = False
        st.session_state.project.log.append("شروع پروژه: هدف ۱۸ ماه، ۱۲۰ میلیارد تومان.")
    
    project = st.session_state.project
    engine = GameEngine(project)
    
    if st.session_state.game_over:
        display_final_result(project)
        st.button("شروع مجدد", on_click=lambda: st.session_state.clear())
        return

    # Display Dashboard
    display_dashboard(project)
    
    st.markdown("---")
    
    # Display Decisions
    current_month = project.current_month
    
    if current_month <= project.scope_target and not st.session_state.game_over:
        
        st.subheader(f"🎯 چالش ماه {current_month}: {engine.phases[current_month-1]}")
        
        options = get_decision_options(current_month)
        
        # نمایش گزینه ها به صورت دکمه
        col_btns = st.columns(len(options))
        keys = list(options.keys())
        
        for i, key in enumerate(keys):
            option = options[key]
            
            # نمایش تاثیرات تصمیم در دکمه
            cost_val = option.get('cost', 0)
            time_val = option.get('time', 0)
            morale_val = option.get('morale', 0)
            
            cost_label = f"💰 {cost_val / 1_000_000_000:+.1f} B"
            time_label = f"⏳ {time_val:+.1f} M"
            morale_label = f"❤️ {morale_val:+.0f}"

            full_label = f"{option['desc']}\n\n ({cost_label}, {time_label}, {morale_label})"

            # استفاده از on_click برای فراخوانی هندلر و rerun 
            if col_btns[i].button(full_label, key=f"btn_{current_month}_{key}", 
                                  on_click=handle_decision_click, args=(key,)):
                # st.rerun() در داخل on_click هندلر فراخوانی می شود
                pass 

    # Display Log
    st.markdown("### گزارش عملکرد و رویدادها")
    
    # نمایش معکوس لاگ
    for entry in reversed(project.log):
        # برجسته سازی لاگ ها برای خوانایی بهتر
        if "🚨" in entry:
            st.error(entry, icon="🚨")
        elif "⚠️" in entry:
            st.warning(entry, icon="⚠️")
        elif entry.startswith("--- 🏗️"):
            st.info(entry)
        elif entry.startswith("✅"):
            st.success(entry, icon="✅")
        else:
            st.write(entry)
        

if __name__ == "__main__":
    main()