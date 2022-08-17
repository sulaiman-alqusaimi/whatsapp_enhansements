import appModuleHandler
import api
from scriptHandler import script
from ui import message
import controlTypes
from keyboardHandler import KeyboardInputGesture
import addonHandler
import os
from gui import SettingsPanel, NVDASettingsDialog, guiHelper
import wx
import config


addonHandler.initTranslation()




spec = {
	"unread_focus": "integer(default=0)",
	"ignore_number": "boolean(default=true)"
}
config.confspec["whatsapp_enhansements"] = spec



class SettingsPanel(SettingsPanel):
	title = "whatsapp enhansements"
	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.ignoreNumber = sHelper.addItem(wx.CheckBox(self, -1, _("ignore reading phone number for unknown contacts"), name="ignore_number"))
		self.ignoreNumber.Value = config.conf["whatsapp_enhansements"]["ignore_number"]
		sHelper.addItem(wx.StaticText(self, -1, _("focus position for the unread shortcut")))
		self.positions = sHelper.addItem(wx.Choice(self, -1, choices=[_("The first unread message"), _("messages count")], name="unread_focus"))
		self.positions.Selection = config.conf["whatsapp_enhansements"]["unread_focus"]
	def postInit(self):
		self.ignoreNumber.SetFocus()
	def onSave(self):
		for control in self.GetChildren():
			if type(control) == wx.CheckBox:
				config.conf["whatsapp_enhansements"][control.Name] = control.Value
			elif type(control) == wx.Choice:
				config.conf["whatsapp_enhansements"][control.Name] = control.Selection

class AppModule(appModuleHandler.AppModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		NVDASettingsDialog.categoryClasses.append(SettingsPanel)
		self.message = None
	def find(self, automationId):
		fg = api.getForegroundObject().children[1]
		for obj in fg.children:
			if obj.UIAAutomationId == automationId:
				return obj

	@script(
		gesture="kb:alt+t", 
		description=_("read the chat subtitle"), 
		category="whatsapp")
	def script_subtitles(self, gesture):
		obj = self.find("TitleButton")
		if obj:
			message(", ".join([o.name for o in obj.children]))
		else:
			gesture.send()

	@script(
		gesture="kb:alt+i", 
		description=_("open chat info"), 
		category="whatsapp")
	def script_info(self, gesture):
		obj = self.find("TitleButton")
		if obj:
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:control+o", 
		description=_("Attach item"), 
		category="whatsapp")
	def script_attach(self, gesture):
		obj = self.find("AttachButton")
		if obj:
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:alt+u", 
		description=_("go to the unread messages section"), 
		category="whatsapp")
	def script_unread(self, gesture):
		def search(txt):
			words = ["غير مقرو", "unread"]
			for word in words:
				if txt.find(word) != -1:
					return word
			return -1
		obj = self.find("ListView")
		if obj:
			for msg in obj.children[::-1]:
				if len(msg.children) == 1 and search(msg.name) != -1:
					msg.next.setFocus() if config.conf["whatsapp_enhansements"]["unread_focus"] == 0 else msg.setFocus()
					break
			else:
				message("لا توجد رسائل جديدة غير مقروءة")
		else:
			gesture.send()

	@script(
		gesture="kb:alt+m",
		description=_("go to the messages list"),
		category="whatsapp")

	def script_messagesList(self, gesture):
		obj = self.find("ListView")
		if obj:
			obj.lastChild.setFocus() if obj.childCount > 0 else obj.setFocus()
		else:
			gesture.send()


	@script(
		gesture="kb:alt+c",
		description=_("go to the chats list"),
		category="whatsapp")
	def script_chatsList(self, gesture):
		obj = self.find("ChatList")

		if obj:
			for child in obj.children:
				if any([i.UIAAutomationId == "ChatsListItem" for i in child.children]):
					chats = child
					break
			else:
				gesture.send()
				return


			for chat in chats.children:
				if controlTypes.STATE_SELECTED in chat.states:
					chat.setFocus()
					break
			else:
				obj.setFocus()
		else:
			gesture.send()

	@script(
		gesture="kb:control+n",
		description=_("new chat"),
		category="whatsapp")
	def script_newChat(self, gesture):
		obj = self.find("NewConvoButton")
		if obj:
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:alt+e",
		description=_("go to the typing message text field"),
		category="whatsapp")
	def script_messageField(self, gesture):

		if not self.message and api.getFocusObject().UIAAutomationId == "TextBox":
			self.find("ListView").children[-1].setFocus()
		elif self.message and api.getFocusObject().UIAAutomationId == "TextBox":
			messages = self.find("ListView")
			try:
				index = messages.children.index(self.message)
				messages.children[index].setFocus()
			except ValueError:
				messages.children[-1].setFocus()
				self.message = None
		elif api.getFocusObject().UIAAutomationId == "BubbleListItem":
			self.message = api.getFocusObject()
			self.find("TextBox").setFocus()
		else:
			obj = self.find("TextBox")
			obj.setFocus() if obj else gesture.send()

	@script(
		gesture="kb:control+r",
		description=_("record voice notes"),
		category="whatsapp")
	def script_record(self, gesture):
		txt = self.find("TextBox")
		obj = self.find("RightButton") or self.find("PttSendButton")
		if obj and  (obj.UIAAutomationId == "RightButton" and obj.firstChild.name == "\ue720") or obj.UIAAutomationId == "PttSendButton":
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:control+shift+r",
		description=_("delete voice notes"),
		category="whatsapp")
	def script_recordDelete(self, gesture):
		obj = self.find("PttDeleteButton")
		if obj:
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:alt+shift+r",
		description=_("pause/resume voice note recording"),
		category="whatsapp")
	def script_recordPauseResume(self, gesture):
		obj = self.find("PttPauseButton") or self.find("PttResumeButton")
		if obj:
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:alt+o", 
		description=_("Activate the more options menu"), 
		category="whatsapp")
	def script_options(self, gesture):
		obj = self.find("SettingsButton")
		if obj:
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:alt+shift+c", 
		description=_("Press audio call button"), 
		category="whatsapp")
	def script_audiocall(self, gesture):
		obj = self.find("AudioCallButton")
		if obj:
			message(_("Calling. Please wait"))
			obj.doAction()
		else:
			gesture.send()

	@script(
		gesture="kb:alt+shift+v", 
		description=_("Press video call button"), 
		category="whatsapp")
	def script_videoCall(self, gesture):
		obj = self.find("VideoCallButton")
		if obj:
			message(_("Calling. Please wait"))
			obj.doAction()
		else:
			gesture.send()



	@script(
		gesture="kb:alt+shift+n",
		description=_("toggle reading number for unknown contacts behaviour"),
		category="whatsapp")
	def script_togleIgnoringNumbers(self, gesture):
		config.conf["whatsapp_enhansements"]["ignore_number"] = not config.conf["whatsapp_enhansements"]["ignore_number"]
		if config.conf["whatsapp_enhansements"]["ignore_number"]:
			message(_("ignore reading numbers for unknown contacts is on"))
		else:
			message(_("ignore reading numbers for unknown contacts is off"))

	def event_gainFocus(self, obj, nextHandler):
		if obj.name in ("WhatsApp.GroupParticipantsItemVm", "WhatsApp.ChatListMessageSearchCellVm", "WhatsApp.ChatListGroupSearchCellVm", "WhatsApp.Pages.Recipients.UserRecipientItemVm"):
			obj.name = ", ".join([m.name for m in obj.children])
		elif obj.UIAAutomationId == "MuteDropdown":
			obj.name = obj.children[0].name
		elif obj.UIAAutomationId == "ThemeCombobox":
			obj.name = obj.previous.name +" "+ obj.firstChild.children[1].name
		elif obj.name == "WhatsApp.Design.ThemeData":
			obj.name = obj.children[1].name
		elif obj.name == "\ue8bb":
			obj.name = _("Cancel reply")
		elif obj.UIAAutomationId == "SendMessages":
			obj.name = _(obj.previous.name +": "+ obj.firstChild.name)
		elif obj.UIAAutomationId == "EditInfo":
			obj.name = _(obj.previous.name +": "+ obj.firstChild.name)
		elif obj.name == "WhatsApp.Design.LightBoxExtendedTextItemVm":
			obj.name = obj.children[0].name
		elif obj.UIAAutomationId in ("NewMessagesNotificationSwitch", "WhenWAClosedSwitch"):
			obj.name = obj.previous.name
		elif obj.UIAAutomationId == "BubbleListItem":
			if config.conf["whatsapp_enhansements"]["ignore_number"]:
				notificationName = None
				name = None
				for item in obj.children:
					if name is None and item.UIAAutomationId == "NameTextBlock":
						name = item.name
						continue
					if notificationName is None and item.UIAAutomationId == "PushNameTextBlock":
						notificationName = item.name

				if notificationName:
					obj.name = obj.name.replace(name, "")
		nextHandler()
	def terminate(self):
		NVDASettingsDialog.categoryClasses.remove(SettingsPanel)