#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Created on Jun 1, 2012

@author: kaganj
'''

'''TODO: only allow numeric input
         add led timer and alarm
         temperature digitally displayed in each meter
         thread the beginning method and the GUI
         Add a keyboard popup for user entry
         drop down that allows changing brew
         drop down that accepts .xml file'''
import wx
import wx.lib.agw.aquabutton as ab
import SpeedMeter as sm
import time
import wx.gizmos as gizmos
from math import pi, sqrt
import time
import thread
import wx.media
import wx.lib.newevent
from serial import *
from threading import Thread
from wx.lib.wordwrap import wordwrap
import re

# This Is For Latin/Greek Symbols I Used In The Demo Only
#wx.SetDefaultPyEncoding('iso8859-1')

class jbrew_controls(wx.Frame):
        
    def __init__(self):   
        self.flag = 0	
        wx.Frame.__init__(self, None, -1, 'Jbrew Controller',
                          wx.DefaultPosition, size=wx.DisplaySize(),
                          style=wx.DEFAULT_FRAME_STYLE | 
                         wx.NO_FULL_REPAINT_ON_RESIZE)   
        
        '''self.bmp = wx.Image("hops.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()'''
        
        self.set_time = 0
        self.timer = None
        self.received_temp = ''
        self.rex_mlt = re.compile('m[0-9][0-9]\.[0-9][0-9]|m[0-2][0-9][0-9]\.[0-9][0-9]')
        self.rex_hlt = re.compile('h[0-9][0-9]\.[0-9][0-9]|h[0-2][0-9][0-9]\.[0-9][0-9]')
	self.rex_he = re.compile('HE[0-9]')
	self.temp1 = 0
        self.temp2 = 0
        self.number = 0
        menubar = wx.MenuBar()
        file = wx.Menu()
        file.Append(22, 'Change Brew', 'Change Title of Brew')
        file.Append(23, 'About', 'About dialog')
        menubar.Append(file, '&File')
    
        self.SetMenuBar(menubar)
        wx.EVT_MENU(self, 22, self.OnChangeBrew)
        wx.EVT_MENU(self, 23, self.OnAboutDialog)
        
        self.panel1 = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        self.panel2 = wx.Panel(self, -1, style=wx.RAISED_BORDER)
        self.panel1.SetBackgroundColour("black")
                
        self.panel3 = wx.Panel(self.panel2, -1, style=wx.SUNKEN_BORDER)
        self.panel4 = wx.Panel(self.panel2, -1, style=wx.RAISED_BORDER)
        self.panel3.SetBackgroundColour("black")
        self.panel4.SetBackgroundColour("black")
        self.panel5 = wx.Panel(self.panel3, -1)
        self.panel6 = wx.Panel(self.panel3, -1)
        self.panel7 = wx.Panel(self.panel3, -1)
        self.panel5.SetBackgroundColour("black")
        self.panel6.SetBackgroundColour("yellow")
        self.panel7.SetBackgroundColour("green")
        
        #Bottom section with clock
        self.panel8 = wx.Panel(self.panel7, -1)
        self.panel9 = wx.Panel(self.panel7, -1)
        self.panel10 = wx.Panel(self.panel7, -1)
        
        self.panel8.SetBackgroundColour("black")
        self.panel9.SetBackgroundColour("black")
        self.panel10.SetBackgroundColour("black")
        '''self.panel10.SetBackgroundColour(None)'''
             
        self.brew_st = wx.StaticText(self.panel1, -1, "BREW: Hoptimistic", (10, 20))
        self.mash_st = wx.StaticText(self.panel5, -1, "MASH MONITOR", (10, 10))
        self.pump_stat_st = wx.StaticText(self.panel8, -1, "PUMP 1 STATUS:", (10, 0))
        self.pump2_stat_st = wx.StaticText(self.panel8, -1, "PUMP 2 STATUS:", (10, 30))
        self.controls_st = wx.StaticText(self.panel4, -1, "CONTROLS", (5, 5))
        self.pump_control = wx.StaticText(self.panel4, -1, "Pump 1", (10, 70))
        self.pump_control2 = wx.StaticText(self.panel4, -1, "Pump 2", (10, 140))
        self.pump_toggle = wx.StaticText(self.panel8, -1, "Off", (240, 0))
        self.pump2_toggle = wx.StaticText(self.panel8, -1, "Off", (240, 30))
        self.he_result = wx.StaticText(self.panel8, -1, "Off", (275, 60))
        self.he_status = wx.StaticText(self.panel8, -1, "HEATING ELEMENT:", (10, 60))
        self.st_temp = wx.StaticText(self.panel4, -1, "Set Target", (10, 235)) 
        self.st_deg = wx.StaticText(self.panel4, -1, "°F", (75, 270))
        self.tc_entry = wx.TextCtrl(self.panel4, -1, "152", (10, 265), (60, 30))
        self.tc_time = wx.TextCtrl(self.panel4, -1, "60", (10, 400), (60, 30))
        self.st_secs = wx.StaticText(self.panel4, -1, "mins", (75, 405))
              
        self.tc_entry.SetMaxLength(3)
        self.tc_entry.SetWindowStyleFlag(wx.TE_RIGHT)
        self.tc_entry.Bind(wx.EVT_LEFT_DOWN, self.OnTempEntry)
        self.tc_time.SetMaxLength(2)
        self.tc_time.SetWindowStyleFlag(wx.TE_RIGHT)
        #self.tc_time.Bind(wx.EVT_CHAR, self.OnTimerEntry)
        self.tc_time.Bind(wx.EVT_LEFT_DOWN, self.OnTimerEntry)
        
        font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self.brew_st.SetFont(font)
        self.mash_st.SetFont(font)
        self.pump_stat_st.SetFont(font)
        self.pump2_stat_st.SetFont(font)
        self.he_status.SetFont(font)
        font = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self.controls_st.SetFont(font)
        font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self.he_result.SetFont(font)
        self.pump_toggle.SetFont(font)
        self.pump2_toggle.SetFont(font)
        font = wx.Font(16, wx.DEFAULT, wx.DEFAULT, wx.BOLD)
        self.pump_control.SetFont(font)
        self.pump_control2.SetFont(font)
        self.st_temp.SetFont(font)
        self.st_deg.SetFont(font)
        self.tc_entry.SetFont(font)
        self.tc_time.SetFont(font)
        self.st_secs.SetFont(font)
        self.brew_st.SetForegroundColour("yellow")
        self.mash_st.SetForegroundColour("yellow")
        self.controls_st.SetForegroundColour("yellow")
        self.pump_stat_st.SetForegroundColour("orange")
        self.pump2_stat_st.SetForegroundColour("orange")
        self.pump_control.SetForegroundColour("yellow")
        self.pump_control2.SetForegroundColour("yellow")
        self.pump_toggle.SetForegroundColour("red")
        self.pump2_toggle.SetForegroundColour("red")
        self.he_status.SetForegroundColour("orange")
        self.he_result.SetForegroundColour("red")
        self.st_temp.SetForegroundColour("yellow")
        self.st_deg.SetForegroundColour("yellow")
        self.st_secs.SetForegroundColour("yellow")
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.panel1, 1, wx.EXPAND)
        bs.Add(self.panel2, 10, wx.EXPAND)
        self.SetSizer(bs)
             
        font = wx.Font(18, wx.DEFAULT, wx.DEFAULT, wx.BOLD)
        
        self.pump_off = 1
        pump_btn = ab.AquaButton(self.panel4, -1, label="On/Off", size=(130, 40), pos=(10, 100))
        pump_btn.SetFont(font)
        pump_btn.SetForegroundColour("black")
        pump_btn.SetBackgroundColor("blue")
        pump_btn.Bind(wx.EVT_BUTTON, self.OnPump)
        
        self.pump2_off = 1
        pump_btn2 = ab.AquaButton(self.panel4, -1, label="On/Off", size=(130, 40), pos=(10, 170))
        pump_btn2.SetFont(font)
        pump_btn2.SetForegroundColour("black")
        pump_btn2.SetBackgroundColor("blue")
        pump_btn2.Bind(wx.EVT_BUTTON, self.OnPump2)
        
        #this is the temperature set button 
        hlt_btn = ab.AquaButton(self.panel4, -1, label="Start", size=(70, 40), pos=(5,300))
        hlt_btn.SetFont(font)
        hlt_btn.SetForegroundColour("black")
        hlt_btn.SetBackgroundColor("blue")
        hlt_btn.Bind(wx.EVT_BUTTON, self.OnSetTemp)
        hlt_btn2 = ab.AquaButton(self.panel4, -1, label="Stop", size=(70, 40), pos=(75,300))
        hlt_btn2.SetFont(font)
        hlt_btn2.SetForegroundColour("black")
        hlt_btn2.SetBackgroundColor("blue")
        hlt_btn2.Bind(wx.EVT_BUTTON, self.OnStopTemp)
        #button that starts the mashing timer 
        ele_btn = ab.AquaButton(self.panel4, -1, label="Start", size=(70, 40), pos=(5, 445))
        ele_btn.SetFont(font)
        ele_btn.SetForegroundColour("black")
        ele_btn.SetBackgroundColor("blue")
        ele_btn.Bind(wx.EVT_BUTTON, self.OnStart)

        #button that stops the mashing timer 
        ele_btn = ab.AquaButton(self.panel4, -1, label="Stop", size=(70, 40), pos=(75, 445))
        ele_btn.SetFont(font)
        ele_btn.SetForegroundColour("black")
        ele_btn.SetBackgroundColor("blue")
        ele_btn.Bind(wx.EVT_BUTTON, self.OnStop)
        
        #button that resets the timer  
        ele_btn = ab.AquaButton(self.panel4, -1, label="Reset", size=(140, 40), pos=(5, 490))
        ele_btn.SetFont(font)
        ele_btn.SetForegroundColour("black")
        ele_btn.SetBackgroundColor("blue")
        ele_btn.Bind(wx.EVT_BUTTON, self.OnReset)
                
        bs_bottom = wx.BoxSizer(wx.HORIZONTAL)
        bs_bottom.Add(self.panel3, 8, wx.EXPAND)
        bs_bottom.Add(self.panel4, 1, wx.EXPAND)
        self.panel2.SetSizer(bs_bottom)
        
        self.mash_meter = sm.SpeedMeter(self.panel6, extrastyle=sm.SM_DRAW_SECTORS | sm.SM_DRAW_HAND 
                                        | sm.SM_DRAW_SECONDARY_TICKS | sm.SM_DRAW_MIDDLE_TEXT
					| sm.SM_DRAW_SPEED_READING)
        # Set The Region Of Existence Of SpeedMeter (Always In Radians!!!!)
        #self.mash_meter.SetAngleRange(-pi/6, 7*pi/6)
        self.mash_meter.SetAngleRange(-pi / 3, 4 * pi / 3)
        # Create The Intervals That Will Divide Our SpeedMeter In Sectors        
        intervals = range(0, 221, 20)
        self.mash_meter.SetIntervals(intervals)

        # Assign The Same Colours To All Sectors (We Simulate A Car Control For Speed)
        # Usually This Is Black
        colours = [wx.BLACK] * 11
        self.mash_meter.SetIntervalColours(colours)

        # Assign The Ticks: Here They Are Simply The String Equivalent Of The Intervals
        ticks = [str(interval) for interval in intervals]
        self.mash_meter.SetTicks(ticks)
        # Set The Ticks/Tick Markers Colour
        self.mash_meter.SetTicksColour(wx.Colour(255, 255, 0))
        # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        self.mash_meter.SetNumberOfSecondaryTicks(3)

        # Set The Font For The Ticks Markers
        self.mash_meter.SetTicksFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Set The Text In The Center Of SpeedMeter
        self.mash_meter.SetMiddleText("Mash Temp")
        # Assign The Colour To The Center Text
        self.mash_meter.SetMiddleTextColour(wx.WHITE)
        # Assign A Font To The Center Text
        self.mash_meter.SetMiddleTextFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        # Set The Default Speed Reading 
        self.mash_meter.SetSpeedReading(self.mash_meter.GetSpeedValue())
        # Assign The Font to the Speed Reading
        self.mash_meter.SetSpeedReadingFont(wx.Font(22, wx.SWISS, wx.NORMAL, wx.BOLD))
        # Assign The Color to the Speed Reading
        self.mash_meter.SetSpeedReadingColour(wx.WHITE)
        # Set The Colour For The Hand Indicator
        self.mash_meter.SetHandColour(wx.Colour(255, 50, 0))

        # Do Not Draw The External (Container) Arc. Drawing The External Arc May
        # Sometimes Create Uglier Controls. Try To Comment This Line And See It
        # For Yourself!
        self.mash_meter.DrawExternalArc(True)
        
        self.mash_meter.SetSpeedValue(100)
        
        self.hlt_meter = sm.SpeedMeter(self.panel6, extrastyle=sm.SM_DRAW_SECTORS | sm.SM_DRAW_HAND 
                                        | sm.SM_DRAW_SECONDARY_TICKS | sm.SM_DRAW_MIDDLE_TEXT
					| sm.SM_DRAW_SPEED_READING)
        # Set The Region Of Existence Of SpeedMeter (Always In Radians!!!!)
        #self.hlt_meter.SetAngleRange(-pi/6, 7*pi/6)
        self.hlt_meter.SetAngleRange(-pi / 3, 4 * pi / 3)
        # Create The Intervals That Will Divide Our SpeedMeter In Sectors        
        intervals = range(0, 221, 20)
        self.hlt_meter.SetIntervals(intervals)

        # Assign The Same Colours To All Sectors (We Simulate A Car Control For Speed)
        # Usually This Is Black
        colours = [wx.BLACK] * 11
        self.hlt_meter.SetIntervalColours(colours)

        # Assign The Ticks: Here frameThey Are Simply The String Equivalent Of The Intervals
        ticks = [str(interval) for interval in intervals]
        self.hlt_meter.SetTicks(ticks)
        # Set The Ticks/Tick Markers Colour
        self.hlt_meter.SetTicksColour(wx.Colour(255, 255, 0))
        # We Want To Draw 5 Secondary Ticks Between The Principal Ticks
        self.hlt_meter.SetNumberOfSecondaryTicks(3)

        # Set The Font For The Ticks Markers
        self.hlt_meter.SetTicksFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Set The Text In The Center Of SpeedMeter
        self.hlt_meter.SetMiddleText("HLT")
        # Assign The Colour To The Center Text
        self.hlt_meter.SetMiddleTextColour(wx.WHITE)
        # Assign A Font To The Center Text
        self.hlt_meter.SetMiddleTextFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Set The Default Speed Reading 
        self.mash_meter.SetSpeedReading(self.mash_meter.GetSpeedValue())
        
        # Assign The Color to the Speed Reading
        self.hlt_meter.SetSpeedReading(self.mash_meter.GetSpeedValue())
        
        # Assign The Font to the Speed Reading
        self.hlt_meter.SetSpeedReadingFont(wx.Font(22, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        # Assign The Color to the Speed Reading
        self.hlt_meter.SetSpeedReadingColour(wx.WHITE)
        
        # Set The Colour For The Hand Indicator
        self.hlt_meter.SetHandColour(wx.Colour(255, 50, 0))
        
        # Do Not Draw The External (Container) Arc. Drawing The External Arc May
        # Sometimes Create Uglier Controls. Try To Comment This Line And See It
        # For Yourself!
        self.hlt_meter.DrawExternalArc(True)

        # Set The Current Value For The SpeedMeter
        self.hlt_meter.SetSpeedValue(100)
        bs_meters = wx.BoxSizer(wx.VERTICAL)
        bs_meters.Add(self.panel5, 0, wx.EXPAND)
        bs_meters.Add(self.panel6, 8, wx.EXPAND)
        bs_meters.Add(self.panel7, 2, wx.EXPAND)
        self.panel3.SetSizer(bs_meters)
        
        hbs_meters = wx.BoxSizer(wx.HORIZONTAL)
        hbs_meters.Add(self.mash_meter, 1, wx.EXPAND)
        hbs_meters.Add(self.hlt_meter, 1, wx.EXPAND)
        self.panel6.SetSizer(hbs_meters)
        
        #begin led timer section
        self.led = gizmos.LEDNumberCtrl(self.panel9, -1, (100, 0), (200, 50), gizmos.LED_ALIGN_CENTER)
        #self.OnTimer(None)
        self.led.SetValue("00:00:00")
        #self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Centre()
        #end led timer
        '''wx.EVT_PAINT(self.panel10, self.OnBmp)'''
            
        bs_timer = wx.BoxSizer(wx.HORIZONTAL)
        bs_timer.Add(self.panel8, 1, wx.EXPAND)
        bs_timer.Add(self.panel9, 1, wx.EXPAND)
        bs_timer.Add(self.panel10, 1, wx.EXPAND)
        self.panel7.SetSizer(bs_timer)
        wx.CallAfter(self.OnInitialOpen)
        
    def OnChangeBrew(self, event):
        '''This section for the change name dialog box'''
        useMetal = False
        dlg = NameDialog(self, -1, "Change Brew Name", size=(350, 200),
                         #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
                         style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
                         useMetal=useMetal,
                         )
        dlg.CenterOnScreen()
        
        # this does not return until the dialog is closed.
        val = dlg.ShowModal()
        
        if val == wx.ID_OK:
            dlg.SetBrewName()

        dlg.Destroy()
        
    def OnAboutDialog(self, evt):
        licenseText = "GPL"
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "JBrew Controls"
        info.Version = "1.0"
        info.Copyright = "(C) 2012 JBrew Home Brewery"
        info.Description = wordwrap(
            "\"JBrew Controls\" is a program that uses an Arduino micro controller "
            "to interface with food grade pumps, temperature sensors, and a heating element "
            "in a Heat Exchange Recirculating Mashing System (HERMS). "
            "\n\nTo use \"Jbrew Controls\", simply select file->Change Brew Name to change "
            "the name of the Brew to your name, then enter a target mashing temperature and "
            "corresponding mashing time in the right control panel. Hit \"Start\" and the timer "
            "plus the Proportional Integral Differential (PID) closed loop feedback system will "
            "take care of the temperature control process for you. "
            "\n\n\"Jbrew Controls\" was written in wx Python, and the SpeedMeter control module "
            "written by Andrea Gavana, was used to aide in producing the meter drawings for the "
            "mash and HLT meters.", 350, wx.ClientDC(self))
        info.WebSite = ("Coming Soon", "Jbrew Controls web monitor")
        info.Developers = [ "Jordan Kagan - Lead Developer",
                            "Andrea Gavana - SpeedMeter controls module",
                          ]

        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
    
    def OnSetTemp(self, event):    
        ser.write(self.tc_entry.GetValue() + "\n")
   	 
    def OnStopTemp(self, event):
	print "stopping"
	ser.write("3\n")
    
    def OnBmp(self, event):
        dc = wx.PaintDC(self.panel10)
        dc = wx.BufferedDC(dc)
        '''dc.DrawBitmap(self.bmp, 100, 10, True)'''    

    def OnStart(self, event):
        
        self.timer = wx.Timer(self, -1)
        self.timer.Start(1000)
        temp_set = self.tc_entry
        timer_set = self.tc_time
        '''temp = temp_set.GetValue()'''
        time = timer_set.GetValue()
        
        if(self.set_time == 0):
            self.time_enter_sec = int(time) * 60
            self.set_time = 1
       
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        
    def OnStop(self, event):
        
        if self.timer:
            self.timer.Stop()
        else:
            event.Skip()
    
    def OnReset(self, event):
        
        self.led.SetValue("00:00:00")
        self.set_time = 0
        self.timer = None
        
    def OnTimer(self, event):
        
        led_hours = self.time_enter_sec / 3600
        
        led_mins = (self.time_enter_sec % 3600) / 60
       
        led_secs = (self.time_enter_sec % 3600) % 60
        
        if(led_hours == 0 and led_mins == 0 and led_secs == 0):
            self.timer.Stop()
        led_time = "%02s:%02s:%02s" % (str(led_hours).zfill(2), str(led_mins).zfill(2), str(led_secs).zfill(2))
        self.led.SetValue(led_time)
        self.time_enter_sec = self.time_enter_sec - 1
        
    def OnInitialOpen(self):
        for ii in range(220):
            self.hlt_meter.SetSpeedValue(ii)
            self.hlt_meter.SetSpeedReading(ii)
            self.mash_meter.SetSpeedValue(ii)
            self.mash_meter.SetSpeedReading(ii)
            wx.MilliSleep(1)
        wx.MilliSleep(500)
        current = 220
        for ii in range(220):
            current = current - 1
            self.hlt_meter.SetSpeedValue(current)
            self.hlt_meter.SetSpeedReading(ii)
            self.mash_meter.SetSpeedValue(current)
            self.mash_meter.SetSpeedReading(ii)
            wx.MilliSleep(10)
        Thread(target=self.receiving, args=(ser,)).start()
    
    def OnTimerEntry(self, event):
        enter_t = MyEntry(self, -1, 'Enter The Preset Time', 0)
        enter_t.Show(True)
    
    def OnTempEntry(self, event):
        enter_t = MyEntry(self, -1, 'Enter The Target Temperature', 1)
        enter_t.Show(True)
  
    def OnPump(self, event):
        
        if  self.pump_off == 1:
            self.pump_toggle.SetLabel("On")
            self.pump_toggle.SetForegroundColour("blue")
            ser.write("1\n")
            self.pump_off = 0 
	else:
            self.pump_toggle.SetLabel("Off")
            self.pump_toggle.SetForegroundColour("red")
            ser.write("1\n")
            self.pump_off = 1 
    
    def OnPump2(self, event):
        
        if  self.pump2_off == 1:
            self.pump2_toggle.SetLabel("On")
            self.pump2_toggle.SetForegroundColour("blue")
            ser.write("2\n")
            self.pump2_off = 0 
        else:
            self.pump2_toggle.SetLabel("Off")
            self.pump2_toggle.SetForegroundColour("red")
            ser.write("2\n")
            self.pump2_off = 1            
    def OnHeatOn(self):
	self.he_result.SetLabel("On")
	self.he_result.SetForegroundColour("blue")
    
    def OnHeatOff(self):
	self.he_result.SetLabel("Off")
	self.he_result.SetForegroundColour("red")
 
    def receiving(self, ser):
        
        buffer = ''
        while True:
	# last_received = ser.readline()
	    #buffer += ser.read(ser.inWaiting())
	    buffer = ser.readline()
	    if '\n' in buffer:
		self.lines = buffer.split('\n')
                self.received_temp = self.lines[-2]
            	m = re.match(self.rex_mlt, self.received_temp)
       	    	n = re.match(self.rex_hlt, self.received_temp)
            	h = re.match(self.rex_he, self.received_temp)
	    	if m is not None:
		    temp = float(m.group(0)[1:])
		    wx.CallAfter(self.hlt_meter.SetSpeedValue, temp)
                    wx.CallAfter(self.hlt_meter.SetSpeedReading, temp)
	    	
	        elif n is not None:
                    temp = float(n.group(0)[1:])
                    wx.CallAfter(self.mash_meter.SetSpeedValue, temp)
                    wx.CallAfter(self.mash_meter.SetSpeedReading, temp)

		elif h is not None:
		    if h.group(0)[2] == '1':
                    	wx.CallAfter(self.OnHeatOn)
		    
		    if h.group(0)[2] == '0':
                    	wx.CallAfter(self.OnHeatOff)
	    		
		else:
		    continue

class NameDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            useMetal=False,
            ):
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "You Can Change The Brew Name")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Brew Name:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.text = wx.TextCtrl(self, -1, "", size=(80,-1))
        box.Add(self.text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button(self, wx.ID_OK)
        #btn.Bind(wx.EVT_BUTTON, self.SetBrewName)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
            
    def SetBrewName(self):
        name = self.text.GetValue()
        frame.brew_st.SetLabel("BREW: " + name)
        
class MyEntry(wx.Frame):
     def __init__(self, parent, id, title, type):
         if type == 0:
             self.type = 0
         elif type == 1:
             self.type = 1
         wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(300, 250))
         self.formula = False
         sizer = wx.BoxSizer(wx.VERTICAL)
         self.display = wx.TextCtrl(self, -1, '',  style=wx.TE_RIGHT)
         sizer.Add(self.display, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 4)
 
         gs = wx.GridSizer(4, 3, 3, 3)
         gs.AddMany([(wx.Button(self, 1, '1'), 0, wx.EXPAND),
                         (wx.Button(self, 2, '2'), 0, wx.EXPAND),
                         (wx.Button(self, 3, '3'), 0, wx.EXPAND),
                         (wx.Button(self, 4, '4'), 0, wx.EXPAND),
                         (wx.Button(self, 5, '5'), 0, wx.EXPAND),
                         (wx.Button(self, 6, '6'), 0, wx.EXPAND),
                         (wx.Button(self, 7, '7'), 0, wx.EXPAND),
                         (wx.Button(self, 8, '8'), 0, wx.EXPAND),
                         (wx.Button(self, 9, '9'), 0, wx.EXPAND),
                         (wx.Button(self, 10, '0'), 0, wx.EXPAND),
                         (wx.Button(self, 11, 'Back'), 0, wx.EXPAND),
                         (wx.Button(self, 12, 'Enter'), 0, wx.EXPAND)])
 
         sizer.Add(gs, 1, wx.EXPAND)
 
         self.SetSizer(sizer)
         self.Centre()
 
         self.Bind(wx.EVT_BUTTON, self.OnBackspace, id=11)
         self.Bind(wx.EVT_BUTTON, self.OnClose, id=12)
         self.Bind(wx.EVT_BUTTON, self.OnSeven, id=7)
         self.Bind(wx.EVT_BUTTON, self.OnEight, id=8)
         self.Bind(wx.EVT_BUTTON, self.OnNine, id=9)
         self.Bind(wx.EVT_BUTTON, self.OnFour, id=4)
         self.Bind(wx.EVT_BUTTON, self.OnFive, id=5)
         self.Bind(wx.EVT_BUTTON, self.OnSix, id=6)
         self.Bind(wx.EVT_BUTTON, self.OnOne, id=1)
         self.Bind(wx.EVT_BUTTON, self.OnTwo, id=2)
         self.Bind(wx.EVT_BUTTON, self.OnThree, id=3)
         self.Bind(wx.EVT_BUTTON, self.OnZero, id=10)
 
     def OnBackspace(self, event):
         formula = self.display.GetValue()
         self.display.Clear()
         self.display.SetValue(formula[:-1])
	
     def OnClose(self, event):
	 value = self.display.GetValue()
         if self.type == 0 and int(value) >= 100:
             self.OnEntryError(event)
             self.Close()
         elif self.type == 1 and int(value) >= 212:
             self.OnTempEntryError(event)
             self.Close()
         else:
             
             if self.type == 0:
                 frame.tc_time.SetValue(value)
                 self.Close()
             else:
                 frame.tc_entry.SetValue(value)
                 self.Close()
                     
     def OnZero(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('0')
 
     def OnOne(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('1')
 
     def OnTwo(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('2')
 
     def OnThree(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('3')
 
     def OnFour(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('4')
 
     def OnFive(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('5')
 
     def OnSix(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('6')
 
     def OnSeven(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('7')
 
     def OnEight(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('8')
 
     def OnNine(self, event):
         if self.formula:
             self.display.Clear()
             self.formula = False
         self.display.AppendText('9')
     
     def OnEntryError(self, event):
         dlg = wx.MessageDialog(self, 'Entry must be less than 100 minutes!',
                               'Error!',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
         dlg.ShowModal()
         dlg.Destroy()
     
     def OnTempEntryError(self, event):
         dlg = wx.MessageDialog(self, 'Entry must be less than 212°F (Boiling) !',
                               'Error!',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
         dlg.ShowModal()
         dlg.Destroy()
    
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = jbrew_controls()
    ser = Serial(
	#port="/dev/ttyACM0",
        port=None,
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
        timeout=0.1,
        xonxoff=0,
        rtscts=0,
        interCharTimeout=None
    )
    frame.Show()
    app.MainLoop()    
