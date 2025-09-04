#views.py

import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from home.utils import responses 
from home.models import Player, Question, Score
import random
from django.db.models import F

def home(request):
    is_player_logged_in = 'player_id' in request.session
    return render(request, 'home/home.html', {'is_player_logged_in': is_player_logged_in})


def login(request): # This is working fine don't touch it.
    if request.method == "POST":
        username = request.POST.get('username')   # CMS ID for player OR username for admin
        password = request.POST.get('password')   # Mobile no for player OR admin password

        print(f"Login attempt: {username} / {password}")

        # 1️⃣ Try authenticating as Django Admin/User
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"Admin authenticated: {user.username}")
            auth_login(request, user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": "/redirect-after-login/"})
            
            return redirect('redirect_after_login')

        # 2️⃣ If not an admin → Try authenticating as Player
        try:
            player = Player.objects.get(crewid=username)
            if player.mobile_no == password:   # ✅ password = mobile number
                # Store player ID in session manually
                request.session['player_id'] = player.id
                print(f"Player authenticated: {player.crew_name}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": True, "redirect_url": "/quiz/"})

                return redirect('start_quiz')
            else:
                print("Player password mismatch")
        except Player.DoesNotExist:
            print("No such player")

        # ❌ Authentication failed
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "Invalid username or password"}, status=400)

        return render(request, 'home/login.html', {'error': 'Invalid username or password'})

    return render(request, 'home/login.html')

@login_required # This is working fine don't touch it.
def redirect_after_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_login')   # Admin goes to dashboard
    elif 'player_id' in request.session:
        return redirect('start_quiz')          # Player goes to quiz page
    else:
        return redirect('login')
    

def start_quiz(request):
    if 'player_id' not in request.session:
        return redirect('login')
    is_player_logged_in = 'player_id' in request.session
    return render(request, 'home/quiz_start.html', {'is_player_logged_in': is_player_logged_in})

@login_required
def admin_login(request):
    return render(request, 'home/admin.html')

# Working from Office
def admin_logout(request):
    auth_logout(request)
    request.session.flush()
    return render(request, "home/home.html")

def logout(request):
    auth_logout(request)
    request.session.flush()
    is_player_logged_in = 'player_id' in request.session
    return render(request, "home/home.html", {'is_player_logged_in': is_player_logged_in})


 # This is Working Fine don't touch it.
def quiz(request):
    if 'player_id' not in request.session:
        return redirect('login')
    questions = list(Question.objects.all())
    questions.sort(key=lambda x: x.id)
    random.shuffle(questions)
    formatted_questions = []
    for q in questions:
        options_texts = [q.option_a, q.option_b, q.option_c, q.option_d]
        options_texts = [opt for opt in options_texts if opt]
        random.shuffle(options_texts)
        labels = ['A', 'B', 'C', 'D']
        options = list(zip(labels, options_texts))
        correct_text = getattr(q, f"option_{q.correct_answer.lower()}") if q.correct_answer else None
        formatted_questions.append({
            'id': q.id,
            'question_text': q.question_text,
            'options': options,
            'correct_answer': correct_text,
        })
    is_player_logged_in = 'player_id' in request.session
    return render(request, "home/quiz.html", {"questions": formatted_questions, 'is_player_logged_in': is_player_logged_in})


def submit_quiz(request):
    try:
        score = 0
        results = []
        for q in Question.objects.all():
            selected = request.POST.get(f"q{q.id}")
            correct = getattr(q, f"option_{q.correct_answer.lower()}") if q.correct_answer else None
            if selected == correct:
                score += q.score
                results.append({
                    "question": q.question_text,
                    "status": "correct",
                    "selected": selected,
                    "correct": correct,
                    "special_note": q.special_note or ""
                })
            else:
                results.append({
                    "question": q.question_text,
                    "status": "wrong",
                    "selected": selected or "No Answer",
                    "correct": correct,
                    "special_note": q.special_note or ""
                })
        
        # Save score to DB
        player_id = request.session.get('player_id')
        if request.user.is_authenticated:
            player = get_object_or_404(Player, id=player_id)
            score_obj, created = Score.objects.get_or_create(player=player)
            if created:
                score_obj.total_score = score
            else:
                score_obj.total_score = F('total_score') + score
            score_obj.save()
            score_obj.refresh_from_db()
            
        return responses.success(
            message="Quiz submitted successfully.",
            data={
                "score": score,
                "results": results
            }
        )
    except Exception as e:
        return responses.error(message=str(e))

# this is not working and need to solve it later
def add_player(request):
    if request.method == "POST":
        try:
            player = Player.objects.create(
                crewid=request.POST.get("crewid"),
                crew_name=request.POST.get("crewname"),
                father=request.POST.get("father"),
                emp_code=request.POST.get("emp_no"),
                mobile_no=request.POST.get("mobile_no"),
            )
            return responses.success(
                message=f"Player {player.crew_name} added successfully.",
                data={"id": player.id}
            )
        except Exception as e:
            return responses.error(message=str(e))
    return render(request, "admin.html")


def edit_player_redirect(request):
    pk = request.GET.get("pk")
    if pk:
        return redirect("edit_player", pk=pk)
    return redirect("home/admin.html")


def edit_player(request, pk):
    try:
        player = Player.objects.get(Player, emp_no=pk)

    except Player.DoesNotExist:
        return print("Error edit player:", pk)

    if request.method == "POST":

        player.crewid = request.POST.get("crewid")
        player.crew_name = request.POST.get("crew_name")
        player.father = request.POST.get("father")
        player.mobile_no = request.POST.get("mobile_no")
        player.emp_code = request.POST.get("emp_code")
        player.save()
        return redirect("admin_login")

    return render(request, "home/admin.html",{"player": Player})


def add_bulk_player(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"error": "No file uploaded"}, status=400)
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            df.columns = [c.strip().upper() for c in df.columns]
            for _, row in df.iterrows():
                Player.objects.create(
                    crewid=row.get("CREWID"),
                    crew_name=row.get("CREW NAME"),
                    father=row.get("FATHER"),
                    emp_code=row.get("EMP CODE"),
                    mobile_no=str(row.get("MOBILE NO")).strip(),
                )
            return JsonResponse({"status": "success","msg": "Players added successfully"})
        except Exception as e:
            return JsonResponse({"status": "error","msg": str(e)}, status=500)

    return render(request, "admin.html")


def add_question(request):
    if request.method =="POST":
        try:
            question_text=request.POST.get("question_text")
            category = request.POST.get("category")
            score=request.POST.get("score")
            special_note=request.POST.get("special_note")
            #Options
            option_a=request.POST.get("option_a")
            option_b=request.POST.get("option_b")
            option_c=request.POST.get("option_c")
            option_d=request.POST.get("option_d")
            #Correct Ans
            correct_answer=request.POST.get("correct_answer")
            
            print("DEBUG : ", option_a, option_b, option_c, option_d, correct_answer)
            Question.objects.create(
                question_text=question_text,
                category=category,
                score=score,
                special_note=special_note,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
            )
            print("Questionadded :", question_text,option_a,option_b,option_c,option_d,correct_answer)
            return responses.success(
                message=f"Question{Question.question_text} added successfully.",
            )
        except Exception as e:
            print("Error while creating question :", e)
            return responses.error(message=str(e))
    return render(request, "admin.html")

def add_bulk_questions(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"error": "No file uploaded"}, status=400)
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            df.columns = [c.strip().upper() for c in df.columns]
            for _, row in df.iterrows():
                Question.objects.create(
                    question_text=row.get("QUESTION"),
                    option_a=row.get("OPTION A"),
                    option_b=row.get("OPTION B"),
                    option_c=row.get("OPTION C"),
                    option_d=row.get("OPTION D"),
                    correct_answer=row.get("CORRECT ANSWER"),
                    special_note=row.get("SPECIAL NOTE"),
                )
            return JsonResponse({"status": "success","msg": "Questions added successfully"})
        except Exception as e:
            return JsonResponse({"status": "error","msg": str(e)}, status=500)

    return render(request, "admin.html")


# For Edit Question in data base;

def edit_question_redirect(request):
    pk = request.GET.get("pk")
    if pk:
        return redirect("edit_question", pk=pk)
    return redirect("admin_login")
    

def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == "POST":
        question.question_text = request.POST.get("question_text")
        question.category = request.POST.get("category")
        question.score = request.POST.get("score")
        question.special_note = request.POST.get("special_note")
        question.option_a = request.POST.get("option_a")
        question.option_b = request.POST.get("option_b")
        question.option_c = request.POST.get("option_c")
        question.option_d = request.POST.get("option_d")
        question.correct_answer = request.POST.get("correct_answer")
        question.save()
        return redirect ("admin_login")
    return render(request, "home/admin.html",{"question" : question})

