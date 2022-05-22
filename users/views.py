from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

variables = []

def register(request):
    if request.user.is_authenticated:
        messages.warning(request, f'Вам нужно зарегистрироваться, чтобы просматривать данную страницу.')
        return redirect('register')
    else:
        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get('patronym'):
                    variables.append(form.cleaned_data.get('patronym'))
                    variables.append(form.cleaned_data.get('student_or_lecturer'))
                form.save()
                messages.success(request, f'Аккаунт создан! Теперь вы можете войти. Не забудьте перейти в профиль и указать свои интересы!')
                variables.clear()
                return redirect('login')
        else:
            form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# instance lets forms be filled with existing data u_form = UserUpdateForm(request.POST, instance=request.user)

def profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, f'Профиль был обновлен.')
                return redirect('profile')

        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, 'users/profile.html', context)
    else:
        messages.warning(request, f'Войдите в систему, чтобы просматривать данную страницу')

        return redirect('/login/?next=/profile/')