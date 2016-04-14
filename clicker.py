import tkinter as tk
from idlelib.ToolTip import ToolTip as Tip

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
        self.gear = {}
        self.gear['clicker'] = Gear('clicker', ['Clicks per click: (%d): 1'],
            ['Click again whenever you click.'], [10])
        self.gear['cursor'] = Gear('cursor', ['Auto cursors: (%d): 0'],
            ['Cursors that click all by themselves, once per second!'], [25])
        self.gear['click booster'] = Gear('click booster', ['Multiplicative click booster: (%d): 1']*5,
            ['Doubles your clicks.']*5, [50]*5, limit=5)
        self.gear['cps to click'] = Gear('cps to click', ['Adds a percentage of cps to each click: (%d): 0']*10,
            ['Clicks per second per click!']*10, [200]*10, limit=10)
        self.gear['cps multiplier'] = Gear('cps multiplier', ['Adds a percentage of cps to cps: (%d): 0']*10,
            ['Makes your clicks per second more stronger!']*10, [500]*10, limit=10)
        self.gear['mobster'] = Gear('mobster', ['Mobster: (%d): 0']*5,
            ['A mobster to get a take from each building, when you click.']*5, [5000]*5, limit=5)
        self.gear['noob training'] = Gear('noob training', ['Double noobs\' clicking: (%d): 0']*5,
            ['"See, here\'s how you click things."']*5, [50]*5, limit=5)
        self.gear['orcish pride'] = Gear('orcish pride', ['Goblins get braver with their gremlin brethren: (%d)'],
            ['Adds to your goblins\' clicks per second for every gremlin you have.'], [1000], limit=1)
        self.gear['noob clicker'] = Gear('noob clicker', ['Noob at clicking: (%d): 0'],
            ['A noob at clicking, but they care!'], [15], multiplier=self.gear['noob training'], per_second=1)
        self.gear['gremlin'] = Gear('gremlin', ['A gremlin to click things: (%d): 0'],
            ['Gremlins enjoy clicking. Really.'], [50], per_second=5)
        self.gear['noob gremlin'] = Gear('noob gremlin', ['Empower gremlins per noob owned: (%d): 0'],
            ['NOOB has evolved into GREMLIN!'], [300], limit=1, power_gear=self.gear['gremlin'], empowers=self.gear['noob clicker'])
        self.gear['goblin'] = Gear('goblin', ['A goblin to provide you with clicks: (%d): 0'],
            ['Goblins click more than gremlins.'], [200], per_second=30,
            synergy_unlocked=self.gear['orcish pride'], synergy_building=self.gear['gremlin'])
        self.gear['inclined plane'] = Gear('inclined plane', ['Roll some clicks your way: (%d): 0'],
            ['Observe clicks in slow motion.'], [500], per_second=125)
        self.gear['pulley'] = Gear('pulley', ['Pull some clicks to you: (%d): 0'],
            ['Not frictionless.'], [2000], per_second=750)
        self.gear['lever'] = Gear('lever', ['Pry some clicks up: (%d): 0'],
            ['Archimedes would be proud.'], [10000], per_second=5000)
        self.gear['wedge'] = Gear('wedge', ['Stuff some extra clicks in there: (%d): 0'],
            ['Can I axe you a question?'], [100000], per_second=75000)
        self.gear['elbow grease'] = Gear('elbow grease', ['Click the old-fashioned way: (%d): 0'],
            ['Surprisingly easy.'], [500000], per_second=500000)
        self.gear['steam-powered clicker'] = Gear('steam-powered clicker',
            ['A steam-powered contraption that clicks: (%d): 0'], ["I'm sure it's steampunk. I see at least five clocks."],
            [5000000], per_second=750000)
        self.gear['coal-fired clicker'] = Gear('coal-fired clicker', ['Harness the power of coal to click: (%d): 0'],
            ['Environmentally-friendly coal!'], [10**7], per_second=2*10**7)
        self.gear['electric clicker'] = Gear('electric clicker', ['Electric-powered clicking: (%d): 0'],
            ['This electricity is generated by a donkey turning a magnet.'], [5*10**7], per_second=125*10**6)
        self.gear['digital clicker'] = Gear('digital clicker', ['Precise clicking, because computers: (%d): 0'],
            ['DIGIMAL RESOMOLUTIONS!!!11!'], [5*10**8], per_second=15*10**8)
        self.gear['floppy disk'] = Gear('floppy disk', ['1.44 million clicks: (%d): 0'],
            ['Actually many more clicks than 1.44m.'], [10**9], per_second=4*10**9)
        self.gear['zip disk'] = Gear('zip disk', ['750MB! Remember those?: (%d): 0'],
            ['Neither do I.'], [5*10**9], per_second=3*10**10)
        self.gear['cd'] = Gear('cd', ['Read some clicks from a CD: (%d): 0'],
            ['30 songs of data!'], [10**10], per_second=8*10**10)
        self.gear['DVD'] = Gear('dvd', ['Read some clicks from a DVD: (%d): 0'],
            ['"The Clickening Begins": now on DVD!'], [2*10**10], per_second=2*10**11)
        self.gear['blu-ray'] = Gear('blu-ray', ['1920x1080 clicks, or more!: (%d): 0'],
            ['High-definition digital blue laser wow!'], [3*10**10], per_second=4*10*11)

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

        for gear in self.gear.values():
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
        
        self.update()
    
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
        self.current_click_label.config(text=self.number_formatter(self.current_clicks))
        
    def purchase(self, gear):
        if self.current_clicks >= gear.cost:
            self.current_clicks -= gear.cost
            gear.quantity += 1
            self.current_click_label.config(text=self.number_formatter(self.current_clicks))
            if gear.empowers:
                gear.empowers.empowered += 1
            if gear.limit and gear.quantity >= gear.limit:
                gear.button.config(state=tk.DISABLED,
                    text=gear.button['text'].split(': ')[0] + ': {} (MAX)'.format(gear.quantity))
            else:
                gear.button.config(
                    text=gear.button['text'].split(': ')[0] + ': ({}): {}'.format(gear.cost, gear.quantity))
    
    def update(self):
        self.the_button.config(text='Click the button! Strength:\n' + self.number_formatter(self.click_strength))
        per_second = self.per_second
        self.current_clicks += int(per_second) + self.gear['cursor'].quantity*self.click_strength
        self.current_click_label.config(text=self.number_formatter(self.current_clicks))
        self.per_second_label.config(text=self.number_formatter(int(per_second)))
        self.parent.after(1000, self.update)

root = tk.Tk()
clicker = Clicker(root)
root.mainloop()