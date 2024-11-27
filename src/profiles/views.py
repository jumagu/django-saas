from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def profile_list_view(request, *args, **kwargs):
    context = {
        'object_list': User.objects.filter(is_active=True)
    }
    return render(request, 'profiles/list.html', context)

# -------------------------------------------------------------------------

@login_required
def profile_detail_view(request, username=None, *args, **kwargs):
    user = request.user
    
    # print(
    #     user.has_perm('subscriptions.basic'),
    #     user.has_perm('subscriptions.pro'),
    #     user.has_perm('subscriptions.advanced'),
    #     user.has_perm('subscriptions.basic_ai'),
    # )
    
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    
    context = {
        'object': profile_user_obj,
        'instance': profile_user_obj,
        'owner': is_me,
    }
    
    return render(request, 'profiles/detail.html', context)

# -------------------------------------------------------------------------

@login_required
def profile_view(request, username=None, *args, **kwargs):
    user = request.user
    print('has_perm:auth.view_user', user.has_perm('auth.view_user'))
    print('has_perm:visits.pagevisit', user.has_perm('visits.pagevisit'))

    # <app_label>.view_<model_name>
    # <app_label>.add_<model_name>
    # <app_label>.change_<model_name>
    # <app_label>.delete_<model_name>
    
    # profile_user_obj = User.objects.get(username=username)
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    if is_me:
        if  user.has_perm('visits.pagevisit'):
            # qs = PageVisit.objects.all()
            pass
    return HttpResponse(f'Hello there {username} - {profile_user_obj.id} - {user.id} - {is_me}')