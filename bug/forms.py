from django import forms
from .models import Bug, BugWorkqueueStatusTypes, BugWorkqueueStatus, BugComment, BugPriorityTypes, BugCategoryTypes

class CreateBug(forms.ModelForm):
    title                           = forms.CharField(max_length = 100,                         widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Bug Title'}))
    description                     = forms.CharField(max_length = 4000,                        widget=forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Bug Description'}))
    priority                        = forms.ModelChoiceField(BugPriorityTypes.objects.all(),    widget=forms.Select(attrs={'class':'form-control', 'placeholder': 'Bug Priority'}))
    category                        = forms.ModelChoiceField(BugCategoryTypes.objects.all(),    widget=forms.Select(attrs={'class':'form-control', 'placeholder': 'Bug Category'}))
    requestor                       = forms.CharField(max_length=255,                           widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Your Name'}))
    requestor_email                 = forms.EmailField(max_length=255,                          widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Your Email'}))
    class Meta:
        model = Bug
        fields = [
            'title',          
            'description',    
            'priority',       
            'category',       
            'requestor',      
            'requestor_email',
            ]

class BugCommentForm(forms.ModelForm):
    comment                         = forms.CharField(max_length = 512,     widget=forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Comment'}))
    class Meta:
        model = BugComment
        fields = [
            'comment',                        
            ]

class EmployeeUpdateBug(forms.ModelForm):
    workqueue_status                = forms.ModelChoiceField(BugWorkqueueStatusTypes.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    workqueue_comment               = forms.CharField(max_length=512,                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comment'}))
    class Meta:
        model = BugWorkqueueStatus
        fields = [
            'workqueue_status',             
            'workqueue_comment',            
            ]

class AdminUpdateBug(forms.ModelForm):
    title                           = forms.CharField(max_length = 100,                         widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Bug Title'}))
    description                     = forms.CharField(max_length = 4000,                        widget=forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Bug Description'}))
    priority                        = forms.ModelChoiceField(BugPriorityTypes.objects.all(),    widget=forms.Select(attrs={'class':'form-control', 'placeholder': 'Bug Priority'}))
    category                        = forms.ModelChoiceField(BugCategoryTypes.objects.all(),    widget=forms.Select(attrs={'class':'form-control', 'placeholder': 'Bug Category'}))
    requestor                       = forms.CharField(max_length=255,                           widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Your Name'}))
    requestor_email                 = forms.EmailField(max_length=255,                          widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Your Email'}))
    class Meta:
        model = Bug
        fields = [
            'title',          
            'description',    
            'priority',       
            'category',       
            'requestor',      
            'requestor_email',
            ]

    def __init__(self, *args, **kwargs):
        super(AdminUpdateBug, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'} 


class AdminUpdateComment(forms.ModelForm):
    comment                         = forms.CharField(max_length = 512,     widget=forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Comment'}))
    class Meta:
        model = BugComment
        fields = [
            'comment',                        
            ]

    def __init__(self, *args, **kwargs):
        super(AdminUpdateComment, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'} 

