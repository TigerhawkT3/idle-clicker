import tkinter as tk
from idlelib.ToolTip import ToolTip as Tip
from tkinter import messagebox
import ast
import random

class Gear:
    def __init__(self, name, descriptions, tips, costs, visibilities,
                 visible=False, quantity=0, per_second=0, limit=0,
                 multiplier=0, synergy_unlocked=None, synergy_building=None,
                 power_gear=0, empowered=0, empowers=0, callback=None,
                 achieve_names=None, achieve_built=None, achieve_production=None):
        self.name = name
        self.descriptions = descriptions
        self.tips = tips
        self.costs = costs
        self.visibilities = visibilities
        self.visible = visible
        self.quantity = quantity
        self.per_second = per_second
        self.limit = limit
        self.multiplier = multiplier
        self.synergy_unlocked = synergy_unlocked
        self.synergy_building = synergy_building
        self.power_gear = power_gear
        self.empowered = empowered
        self.empowers = empowers
        self.callback = callback
        self.achieve_built = achieve_built
        self.achieve_production = achieve_production
        self.achieve_names = achieve_names
    
    @property
    def description(self):
        if self.limit and self.quantity < self.limit:
            return self.descriptions[self.quantity]
        return self.descriptions[-1]
    
    @property
    def tip(self):
        if self.limit and self.quantity < self.limit:
            return self.tips[self.quantity]
        return self.tips[-1]
        
    @property
    def cost(self):
        if self.limit:
            if self.quantity < self.limit:
                return self.costs[self.quantity]
            return self.costs[-1]
        return int(self.costs[0] * 1.15**self.quantity)
    
    def calculated_per_second(self, base):
        temp = 0
        if self.synergy_unlocked and self.synergy_unlocked.quantity:
            temp += self.quantity * self.synergy_building.quantity
        if self.power_gear and self.quantity:
            temp += self.power_gear.quantity * self.empowers.quantity
        return temp * base * 0.05
        
class Clicker:
    def __init__(self, parent):
        self.parent = parent
        self.tooltips = {}
        self.the_button = tk.Button(parent, text='Click the button! Strength:\n', width=20, height=5, command=self.increment)
        self.golden_button = tk.Button(parent, text='Activate super\nclicking power!', width=20, height=5, command=self.golden)
        self.current_clicks = 0
        self.cumulative_clicks = 0
        self.purchase_direction = 1
        self.golden_buff_strength = 1 # or 1024
        self.golden_buff_duration = 16 # or 32
        self.golden_button_delay_unit = 60 # or 30
        self.golden_button_duration = 16 # or 32
        self.golden_button_running = lambda: None
        self.gear = {}
        self.achievements = set()
        self.callbacks = {'golden':self.golden}
        
        with open('clicker_gear.txt') as f:
            for line in f:
                d = ast.literal_eval(line)
                self.gear[d['name']] = Gear(**d)
        for gear in self.gear.values():
            if gear.multiplier:
                gear.multiplier = self.gear[gear.multiplier]
            if gear.power_gear:
                gear.power_gear = self.gear[gear.power_gear]
            if gear.empowers:
                gear.empowers = self.gear[gear.empowers]
            if gear.synergy_unlocked:
                gear.synergy_unlocked = self.gear[gear.synergy_unlocked]
            if gear.synergy_building:
                gear.synergy_building = self.gear[gear.synergy_building]
            if gear.callback:
                gear.callback = self.callbacks[gear.callback]

        canvas_width=604
        canvas_height=200
        self.upgrade_frame = tk.Frame(parent)
        self.current_click_label = tk.Label(parent, text='0')
        self.the_button.grid(row=0, column=0)
        self.current_click_label.grid(row=0, column=1)
        self.per_second_label = tk.Label(parent, text='0')
        self.per_second_label.grid(row=0, column=2)
        self.upgrade_frame.grid(row=1, column=1, columnspan=2)
        self.scrollbar = tk.Scrollbar(self.upgrade_frame, orient=tk.VERTICAL)
        self.upgrade_canvas = tk.Canvas(self.upgrade_frame, width=canvas_width, height=canvas_height, yscrollcommand=self.scrollbar.set)
        self.cframe = tk.Frame(self.upgrade_canvas)
        self.cframe.bind("<Configure>", lambda x: self.upgrade_canvas.configure(
            scrollregion=self.upgrade_canvas.bbox('all'), width=canvas_width, height=canvas_height))
        self.cwindow = self.upgrade_canvas.create_window((0,0), window=self.cframe, anchor='nw')
        self.scrollbar.config(command=self.upgrade_canvas.yview)
        self.upgrade_canvas.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky='NS')
        self.parent.bind('<MouseWheel>', lambda x: self.upgrade_canvas.yview_scroll(-1*(x.delta//30), 'units'))

        for gear in sorted(self.gear.values(), key=lambda x: (x.per_second, x.cost)):
            gear.button = tk.Button(self.cframe, width=42, text=gear.description.format(self.number_formatter(gear.cost),
                                                                              self.number_formatter(gear.quantity)),
                                    command=lambda x=gear: self.purchase(x))
            if gear.per_second:
                format_string = '{} - ({}/s)'
                per = self.number_formatter(gear.per_second)
            else:
                format_string = '{}{}'
                per = ''
            gear.tooltip = Tip(gear.button, format_string.format(gear.tip, per))
        
        self.manual_row = -1
        self.auto_row = -1
        
        self.parent.bind('c', lambda x: messagebox.showinfo(title='Cumulative clicks',
            message='Cumulative clicks:\n' + self.number_formatter(self.cumulative_clicks)))
        self.parent.bind('r', self.purchase_toggle)
        
        self.update()
    
    def golden(self):
        self.golden_button.grid_forget()
        self.golden_buff_strength = 1024
        self.parent.after_cancel(self.golden_button_running)
        
        def reduce_click():
            self.golden_buff_strength = 1
        def add_button():
            self.golden_button.grid(row=1, column=0)
            self.golden_button_running = self.parent.after(self.golden_button_duration, remove_button)
            #self.golden_button_running = self.parent.after(1000, remove_button)
        def remove_button():
            self.golden_button.grid_forget()
            self.golden_button_running = self.parent.after(random.randint(3, 5)*self.golden_button_delay_unit*1000, add_button)
            #self.golden_button_running = self.parent.after(3000, add_button)
                
        self.parent.after(self.golden_buff_duration*1000, reduce_click)
        self.parent.after(random.randint(3, 5)*self.golden_button_delay_unit*1000, add_button)
        #self.parent.after(5000, reduce_click)
        #self.parent.after(10000, add_button)
        
    def purchase_toggle(self, event=None):
        self.purchase_direction *= -1
        if self.purchase_direction == 1:
            action = 'purchasing'
        else:
            action = 'refunding'
        messagebox.showinfo(title='Purchase/refund',
            message='You are now {} when you click gear.'.format(action))
    
    @property
    def click_strength(self):
        return int((
                     self.gear['clicker'].quantity + 1 +
                     self.gear['mobster'].quantity *
                     sum(building.quantity for building in self.gear.values() if building.per_second) +
                     self.gear['cps to click'].quantity*0.01*self.per_second
                    ) *
                     2**self.gear['click booster'].quantity * self.golden_buff_strength
                  )
    
    @property
    def base_per_second(self):
        return sum(gear.per_second*gear.quantity*(
            gear.multiplier and 2**gear.multiplier.quantity or 1)*(
            2**gear.empowered
            ) for gear in self.gear.values()
            ) * 1.01**self.gear['cps multiplier'].quantity + per_second
    
    @property
    def per_second(self):
        per_second = base = self.base_per_second
        for gear in self.gear.values():
            per_second += gear.per_second(base)
        return base + per_second
    
    def number_formatter(self, number):
        if number < 10**15:
            return '{:,}'.format(number)
        if number < 10**308:
            return '{:.1e}'.format(number)
        quant = 0
        while number > 10**308:
            quant += 1
            number //= 10**308
        label = '{:.1e}'.format(number)
        base, size = label.split('e+')
        size = int(size) + 308*quant
        return '{}e+{}'.format(base, self.number_formatter(size))
    
    def increment(self):
        self.current_clicks += self.click_strength
        self.cumulative_clicks += self.click_strength
        self.current_click_label.config(text='Current clicks:\n' + self.number_formatter(self.current_clicks))
        
    def purchase(self, gear):
        if self.purchase_direction == 1:
            if self.current_clicks < gear.cost:
                return
            self.current_clicks -= gear.cost * self.purchase_direction
            gear.quantity += self.purchase_direction
        else:
            if not gear.quantity:
                return
            gear.quantity += self.purchase_direction
            self.current_clicks -= gear.cost * self.purchase_direction
        
        self.current_click_label.config(text='Current clicks:\n' + self.number_formatter(self.current_clicks))
        if gear.empowers:
            gear.empowers.empowered += self.purchase_direction
        if gear.callback:
            gear.callback()
        if gear.limit and gear.quantity >= gear.limit:
            gear.button.config(state=tk.DISABLED,
                text=gear.description.format(self.number_formatter(gear.cost), '(MAX)')
                )
        else:
            gear.button.config(
                text=gear.description.format(self.number_formatter(gear.cost), self.number_formatter(gear.quantity))
                )
    
    def check_achievements(self):
        '''
        Checks achievements and adds completed ones to the set. Incomplete.
        '''
        for gear in self.gear.values():
            if gear.achieve_names:
                for name, value in gear.achieve_built:
                    if gear.quantity > value:
                        self.achievements.add(name)
                for name, value in gear.achieve_production:
                    pass # implement this
                        
    
    def update(self):
        #self.check_achievements()
        self.the_button.config(text='Click the button! Strength:\n' + self.number_formatter(self.click_strength))
        per_second = self.per_second
        additional = int(per_second) + self.gear['cursor'].quantity*self.click_strength
        self.current_clicks += additional
        self.cumulative_clicks += additional
        
        for gear in sorted(self.gear.values(), key=lambda x: x.cost):
            if gear.visible:
                continue
            if gear.quantity or gear.visibilities[gear.quantity] > self.cumulative_clicks:
                break
            if gear.per_second:
                self.manual_row += 1
                row = self.manual_row
                column = 1
            else:
                self.auto_row += 1
                row = self.auto_row
                column = 0
            gear.visible = True
            gear.button.grid(row=row, column=column)
        
        self.current_click_label.config(text='Current clicks:\n' + self.number_formatter(self.current_clicks))
        self.per_second_label.config(text='Clicks per second:\n' + self.number_formatter(int(per_second)))
        self.parent.after(1000, self.update)

root = tk.Tk()
clicker = Clicker(root)
root.mainloop()