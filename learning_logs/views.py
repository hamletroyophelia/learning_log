from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

# 导入所需数据相关联的模型
from .models import Topic, Entry
from .forms import TopicForm, EntryForm


# Create your views here.
def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')


# 限制对特定页面的访问,重定向跳转到登录页面
@login_required
def topics(request):
    """显示所有的主题"""
    all_topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': all_topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """显示单个主题及其所有的条目"""
    single_topic = Topic.objects.get(id=topic_id)
    # 确认请求的主题属于当前用户.
    check_topic_owner(single_topic, request.user)

    entries = single_topic.entry_set.order_by('-date_added')
    context = {'topic': single_topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """添加新主题"""
    if request.method != 'POST':
        # 未提交数据:创建一个新表单.
        form = TopicForm()
    else:
        # POST提交的数据:对数据进行处理
        form = TopicForm(data=request.POST)
        if form.is_valid():
            added_new_topic = form.save(commit=False)
            added_new_topic.owner = request.user
            added_new_topic.save()
            return redirect('learning_logs:topics')

    # 显示空表单或指出表单数据无效
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """在特定主题中添加新条目"""
    special_topic = Topic.objects.get(id=topic_id)

    check_topic_owner(special_topic, request.user)

    if request.method != 'POST':
        # 未提交数据:创建一个新表单.
        form = EntryForm()
    else:
        # POST提交的数据:对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            one_new_entry = form.save(commit=False)
            one_new_entry.topic = special_topic
            one_new_entry.save()
            return redirect('learning_logs:topics', topic_id=topic_id)

    # 显示空表单或指出表单数据无效
    context = {'topic': special_topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """编辑既有条目"""
    entry = Entry.objects.get(id=entry_id)
    special_topic = entry.topic

    # 确认请求的条目属于当前用户.
    check_topic_owner(special_topic, request.user)

    if request.method != 'POST':
        # 初次请求(Get):使用当前条目填充表单
        form = EntryForm(instance=entry)
    else:
        # POST提交的数据:对数据进行处理
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=special_topic.id)

    # 显示可编辑的空表单或指出表单数据无效
    context = {'entry': entry, 'topic': special_topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)


def check_topic_owner(check_topic, user):
    """保护页面"""
    """检查请求的主题是否属于当前用户"""
    if check_topic.owner != user:
        raise Http404
