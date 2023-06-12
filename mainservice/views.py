from django.shortcuts import render



def main_page(request):
    return render(
        request,
        'main/main.html'
)

def invite_page(request):
    return render(
        request,
        'main/invite.html'
)

def team_page(request):
    return render(
        request,
        'main/team.html'
)