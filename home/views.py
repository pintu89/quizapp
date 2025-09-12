#views.py
import re
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from home.utils import responses 
from home.models import Player, Question, Score, PlayerAnswer
from django.db.models.functions import Random
import random
from django.db.models import F, Q
from django.contrib import messages

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
                    return responses.success({"Login successful": True, "redirect_url": "/quiz/"})

                return redirect('start_quiz')
            else:
                print("Player password mismatch")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return responses.error({"Invalid Password"}, status=400)
                return render(request, 'home/login.html', {'error': 'Invalid username or password'})
        except Player.DoesNotExist:
            print("No such player")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return responses.error({"Invalid Username"}, status=400)
            return render(request, 'home/login.html', {'error': 'No such player found'})

        # # ❌ Authentication failed
        # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        #     return JsonResponse({"success": False, "error": "Invalid username or password"}, status=400)

        # return render(request, 'home/login.html', {'error': 'Invalid username or password'})

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


def quiz(request):
    if 'player_id' not in request.session:
        return redirect('login')

    selected_category = request.GET.getlist('category')
    question_count = int(request.GET.get('question_count', 15))
    player_id = request.session['player_id']
    player = get_object_or_404(Player, id=player_id)
    answered_ids = PlayerAnswer.objects.filter(player=player).values_list('question_id', flat=True)

    if selected_category and selected_category !=['All']:
        questions = Question.objects.filter(category__in=selected_category).exclude(id__in=answered_ids)   
    else:
        questions = Question.objects.all()    
    questions = questions.exclude(id__in=answered_ids)
    if not questions.exists():
        PlayerAnswer.objects.filter(player=player).delete()
        if selected_category and selected_category !=['All']:
            questions = Question.objects.filter(category__in=selected_category)
        else:
            questions = Question.objects.all()
        
    questions = list(questions)
    random.shuffle(questions)
    questions = questions[:question_count]
    request.session['quiz_questions'] = [q.id for q in questions]
    formatted_questions = []
    for q in questions:
        options_texts = []
        if q.option_a_eng: options_texts.append(q.option_a_eng, q.option_a_hin)
        if q.option_b_eng: options_texts.append(q.option_b_eng, q.option_b_hin)
        if q.option_c_eng: options_texts.append(q.option_c_eng, q.option_c_hin)
        if q.option_d_eng: options_texts.append(q.option_d_eng, q.option_d_hin)
        options_texts = [opt for opt in options_texts if opt]
        random.shuffle(options_texts)
        labels = ['A','B','C','D']
        options = list(zip(labels, options_texts))
        correct_text = getattr(q, f"option_{q.correct_answer.lower()}") if q.correct_answer else None
        formatted_questions.append({
            'id' : q.id,
            'question_eng' : q.question_eng,
            'question_hin' : q.question_hin,
            'options' : options,
            'correct_answer' : correct_text,
        })
    return render(
        request,
        "home/quiz.html",
        {"questions": formatted_questions, 'is_player_logged_in': True}
    )

def submit_quiz(request):
    try:
        score = 0
        results = []
        question_ids = request.session.get('quiz_questions',[])
        questions = Question.objects.filter(id__in=question_ids)
        player_id = request.session.get('player_id')
        if not player_id:
            return responses.error(message="Player not logged in.", status=401) 
        player = get_object_or_404(Player, id = player_id)

        for q in questions:
            selected = request.POST.get(f"q{q.id}")
            correct = getattr(q, f"option_{q.correct_answer.lower()}_eng") if q.correct_answer else None
            is_correct = (selected == correct)

            PlayerAnswer.objects.get_or_create(
                player=player,
                question=q,
                defaults={
                    "selected_answer": selected,
                    "is_correct": is_correct
                }
            )

            if is_correct:
                score += q.score
                results.append({
                    "question" : q.question_eng,
                    "status" : "correct",
                    "selected" : correct,
                    "special_note" : q.special_note or ""
                })
            else:
                results.append({
                    "question" : q.question_eng,
                    "status": "Wrong",
                    "selected" : selected or "No Answer",
                    "correct": correct,
                    "special_note" : q.special_note or ""
                })
        player.score = score
        player.save(update_fields=['score'])
        score_obj, created = Score.objects.get_or_create(player=player)
        if created:
            score_obj.total_score = score
            score_obj.save()
        else:
            score_obj.total_score = F('total_score') + score
            score_obj.refresh_from_db()
        request.session.pop('quiz_questions', None)
        return responses.success(
            message="Quiz submitted successfully.",
            data={
                "score" : score,
                "session_score" : player.score,
                "total_score" : score_obj.total_score,
                "results" : results,
            }
        )
    except Exception as e:
        return responses.error(message=str(e))


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
            question_eng=request.POST.get("question_eng")
            question_hin=request.POST.get("question_hin")
            category = request.POST.get("category")
            score=request.POST.get("score")
            special_note=request.POST.get("special_note")
            #Options
            option_a_eng=request.POST.get("option_a_eng")
            option_b_eng=request.POST.get("option_b_eng")
            option_c_eng=request.POST.get("option_c_eng")
            option_d_eng=request.POST.get("option_d_eng")
            option_a_hin=request.POST.get("option_a_hin")
            option_b_hin=request.POST.get("option_b_hin")
            option_c_hin=request.POST.get("option_c_hin")
            option_d_hin=request.POST.get("option_d_hin")
            #Correct Ans
            correct_answer=request.POST.get("correct_answer")
            Question.objects.create(
                question_eng=question_eng,
                question_hin=question_hin,
                category=category,
                score=score,
                special_note=special_note,
                option_a_eng=option_a_eng,
                option_b_eng=option_b_eng,
                option_c_eng=option_c_eng,
                option_d_eng=option_d_eng,

                option_a_hin=option_a_hin,
                option_b_hin=option_b_hin,
                option_c_hin=option_c_hin,
                option_d_hin=option_d_hin,
                correct_answer=correct_answer,
            )
            print("Questionadded :", question_eng,question_hin,option_a_eng,correct_answer)
            return responses.success(
                message=f"Question{Question.question_eng},{Question.question_hin} added successfully.",
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
            required_cols=["QUESTION","OPTION A","OPTION B","OPTION C","OPTION D","CORRECT ANSWER"]
            for col in required_cols:
                if col not in df.columns:
                    messages.error(request, f"Missing required column: {col}")
                    return JsonResponse({"status": "error","msg": f"Missing required column: {col}"}, status=400)

            added, skipped = 0, 0

            for _, row in df.iterrows():
                q_text = str(row.get("QUESTION")).strip()
                raw_ans = str(row.get("CORRECT ANSWER")).strip().upper()
                match = re.search(r'([A-D])', raw_ans, re.IGNORECASE)
                if match:
                    correct_answer = match.group(1).upper()
                else:
                    correct_answer = ""
                if not q_text:
                    skipped += 1
                    continue
                
                if Question.objects.filter(question_eng__iexact=q_text).exists():
                    skipped += 1
                    continue
                if Question.objects.filter(question_hin_iexact=q_text).exists():
                    skipped +=1
                    continue
        
                try:
                    Question.objects.create(
                        question_eng=row.get("QUESTION"),
                        question_hin=row.get("QUESTION"),
                        option_a_eng=row.get("OPTION A"),
                        option_b_eng=row.get("OPTION B"),
                        option_c_eng=row.get("OPTION C"),
                        option_d_eng=row.get("OPTION D"),

                        option_a_hin=row.get("OPTION A"),
                        option_b_hin=row.get("OPTION B"),
                        option_c_hin=row.get("OPTION C"),
                        option_d_hin=row.get("OPTION D"),
                        correct_answer=correct_answer,
                        special_note=row.get("SPECIAL NOTE"),
                        category=row.get("CATEGORY", "Others"),
                        score=row.get("SCORE", 5),
                    )
                    added += 1
                except Exception as e:
                    print(f"Error adding question at row {skipped}: {e}")
                    continue
            return JsonResponse({"status": "success","msg": f"{added} Questions added successfully"})
        except Exception as e:
            return JsonResponse({"status": "error","msg": str(e)}, status=500)

    return render(request, "admin.html")


# For Edit Question in data base it is not working;

def edit_question_redirect(request):
    pk = request.GET.get("pk")
    if pk:
        return redirect("edit_question", pk=pk)
    return redirect("admin_login")
    

def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == "POST":
        question.question_eng = request.POST.get("question_eng")
        question.question_hin = request.POST.get("question_hin")
        question.category = request.POST.get("category")
        question.score = request.POST.get("score")
        question.special_note = request.POST.get("special_note")
        question.option_a_eng = request.POST.get("option_a_eng")
        question.option_b_eng = request.POST.get("option_b_eng")
        question.option_c_eng = request.POST.get("option_c_eng")
        question.option_d_eng = request.POST.get("option_d_eng")
        question.option_a_hin = request.POST.get("option_a_hin")
        question.option_b_hin = request.POST.get("option_b_hin")
        question.option_c_hin = request.POST.get("option_c_hin")
        question.option_d_hin = request.POST.get("option_d_hin")
        question.correct_answer = request.POST.get("correct_answer")
        question.save()
        return redirect ("admin_login")
    return render(request, "home/admin.html",{"question" : question})



#This is for Play Game Section---->
def Play_Game(request):
    if 'player_id' not in request.session:
        return redirect('login')
    is_player_logged_in = 'player_id' in request.session

    return render(request, 'game/game.html', {'is_player_logged_in': is_player_logged_in})