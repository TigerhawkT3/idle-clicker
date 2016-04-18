import tkinter as tk
from idlelib.ToolTip import ToolTip as Tip
from tkinter import messagebox
import ast

class Gear:
    def __init__(self, name, descriptions, tips, costs, quantity=0, per_second=0, limit=0,
                 multiplier=0, synergy_unlocked=None, synergy_building=None,
                 power_gear=0, empowered=0, empowers=0):
        self.name = name
        self.descriptions = descriptions
        self.tips = tips
        self.costs = costs
        self.quantity = quantity
        self.per_second = per_second
        self.limit = limit
        self.multiplier = multiplier
        self.synergy_unlocked = synergy_unlocked
        self.synergy_building = synergy_building
        self.power_gear = power_gear
        self.empowered = empowered
        self.empowers = empowers
    
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
        
class Clicker:
    def __init__(self, parent):
        self.parent = parent
        self.tooltips = {}
        self.the_button = tk.Button(parent, text='Click the button! Strength:\n', width=20, height=5, command=self.increment)
        self.current_clicks = 0
        self.cumulative_clicks = 0
        self.purchase_direction = 1
        self.gear = {}
        
        with open('clicker_gear.txt') as f:
            for line in f:
                d = ast.literal_eval(line)
                self.gear[d.name] = Gear(**d)
        for gear in self.gear.values():
            if gear.multiplier:
                gear.multiplier = self.gear[gear.multiplier]
            if gear.power_gear:
                gear.power_gear = self.gear[power_gear]
            if gear.empowers:
                gear.empowers = self.gear[empowers]
            if gear.synergy_unlocked:
                gear.synergy_unlocked = self.gear[synergy_unlocked]
            if gear.synergy_building:
                gear.synergy_building = self.gear[synergy_building]

        self.upgrade_frame = tk.Frame(parent)
        self.current_click_label = tk.Label(parent, text='0')
        self.the_button.grid(row=0, column=0)
        self.current_click_label.grid(row=0, column=1)
        self.per_second_label = tk.Label(parent, text='0')
        self.per_second_label.grid(row=0, column=2)
        self.upgrade_frame.grid(row=1, column=1, columnspan=2)
        self.scrollbar = tk.Scrollbar(self.upgrade_frame, orient=tk.VERTICAL)
        self.upgrade_canvas = tk.Canvas(self.upgrade_frame, yscrollcommand=self.scrollbar.set)
        self.cframe = tk.Frame(self.upgrade_canvas)
        self.cframe.bind("<Configure>", lambda x: self.upgrade_canvas.configure(
            scrollregion=self.upgrade_canvas.bbox('all'), width=600, height=200))
        self.cwindow = self.upgrade_canvas.create_window((0,0), window=self.cframe, anchor='nw')
        self.scrollbar.config(command=self.upgrade_canvas.yview)
        self.upgrade_canvas.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky='NS')
        self.parent.bind('<MouseWheel>', lambda x: self.upgrade_canvas.yview_scroll(-1*(x.delta//30), 'units'))

        for gear in sorted(self.gear.values(), key=lambda x: (x.per_second, x.cost)):
            gear.button = tk.Button(self.cframe, text=gear.description % gear.cost,
                                            command=lambda x=gear: self.purchase(x))
            gear.tooltip = Tip(gear.button, gear.tip + ' - (%d/s)' % gear.per_second)
        
        manual_row = -1
        auto_row = -1
        for gear in sorted(self.gear.values(), key=lambda x: x.cost):
            if gear.per_second:
                manual_row += 1
                row = manual_row
                column = 1
            else:
                auto_row += 1
                row = auto_row
                column = 0
            gear.button.grid(row=row, column=column)
        
        self.parent.bind('c', lambda x: messagebox.showinfo(title='Cumulative clicks',
            message='Cumulative clicks:\n' + self.number_formatter(self.cumulative_clicks)))
        self.parent.bind('r', self.purchase_toggle)
        
        self.update()
    
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
                     2**self.gear['click booster'].quantity
                  )
    
    @property
    def per_second(self):
        per_second = base_per_second = sum(gear.per_second*gear.quantity*(
            gear.multiplier and 2**gear.multiplier.quantity or 1)*(
            2**gear.empowered
            ) for gear in self.gear.values())
        for gear in self.gear.values():
            if gear.synergy_unlocked and gear.synergy_unlocked.quantity:
                per_second += gear.quantity * gear.synergy_building.quantity * 0.05 * base_per_second
            if gear.power_gear and gear.quantity:
                per_second += gear.power_gear.quantity * gear.empowers.quantity * base_per_second * 0.05
        return per_second * 1.01**self.gear['cps multiplier'].quantity
    
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
        if gear.limit and gear.quantity >= gear.limit:
            gear.button.config(state=tk.DISABLED,
                text=gear.button['text'].split(': ')[0] + ': {} (MAX)'.format(gear.quantity))
        else:
            gear.button.config(
                text=gear.button['text'].split(': ')[0] + ': ({}): {}'.format(gear.cost, gear.quantity))
    
    def update(self):
        self.the_button.config(text='Click the button! Strength:\n' + self.number_formatter(self.click_strength))
        per_second = self.per_second
        additional = int(per_second) + self.gear['cursor'].quantity*self.click_strength
        self.current_clicks += additional
        self.cumulative_clicks += additional
        self.current_click_label.config(text='Current clicks:\n' + self.number_formatter(self.current_clicks))
        self.per_second_label.config(text='Clicks per second:\n' + self.number_formatter(int(per_second)))
        self.parent.after(1000, self.update)

root = tk.Tk()
clicker = Clicker(root)
root.mainloop()