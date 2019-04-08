from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect

from .forms import SignUpForm

def signup(request):
    """create a singup

    .. note::This code was made by following this tutorial "https://simpleisbetterthancomplex.com/tutorial/2016/06/27/how-to-use-djangos-built-in-login-system.html". Some part of the code is change in order to be able to be integrated to the webapp

    :param request: object that contains metadata about the request.

    :returns: render (a combinations of a given template with a given context dictionary and returns an HttpResponse object with that rendered text.).
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('course')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
