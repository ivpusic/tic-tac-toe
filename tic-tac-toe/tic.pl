:- dynamic(move/2).
:- dynamic(scores/1).

human(x).
computer(o).


win_(a, b, c).
win_(d, e, f).
win_(g, h, i).
win_(a, d, g).
win_(b, e, h).
win_(c, f, i).
win_(a, e, i).
win_(c, e, g).

% true if A B C are winning squares -> user or computer is won game
win(A, B, C) :-
	(
	 win_(A, B, C), !;
	 win_(A, C, B), !;
	 win_(B, A, C), !;
	 win_(B, C, A), !;
	 win_(C, A, B), !;
	 win_(C, B, A), !
	).

% true if all squares are filled
filled :-
	move(a, _), move(b, _), move(c, _),
	move(d, _), move(e, _), move(f, _),
	move(g, _), move(h, _), move(i, _).

% true if Winner (eg. x or o) is win
winner(Winner) :-
	move(X, Winner),
	move(Y, Winner),
	move(Z, Winner),
	win(X, Y, Z).


% if Old is o New will be x 
switch_turns(Old, New) :-
	member(Old, [o,x]),
	member(New, [o,x]),
	Old \= New.

%used for some in game-over
tie :-
	winner(_),!,fail;
	filled.

% list of free squares
free(Square) :-
	member(Square, [a,b,c,d,e,f,g,h,i]),
	\+ move(Square, _).
% remark: \+ -> meaining is -> is not provable

% predicate for enter player move -> if square is free, mark square 
user_enter(Turn, Input) :-
	human(Turn),
	repeat,
	member(Input, [a,b,c,d,e,f,g,h,i]),
	free(Input).

% if computer can win, prefet that move
enter(Square, Turn) :-
	computer(Turn),
	free(Square),
	move(X, Turn),
	move(Y, Turn),
	win(Square, X, Y),
	!.

% block winning move
enter(Square, Turn) :-
	computer(Turn),
	switch_turns(Turn, Op),
	move(X, Op),
	move(Y, Op),
	win(Square, X, Y),
	free(Square).

% take two in a row if we can
enter(Square, Turn) :-
	computer(Turn),
	move(X, Turn),
	free(Square),
	free(Y),
	win(Square, X, Y),
	!.

% if we can take middle, take it
enter(Square, Turn) :- 
	computer(Turn),
	free(e),
	Square = e,
	!.

% else take whatever move
enter(Square, Turn) :-
	computer(Turn),
	free(Square),
	!.

% ----- Draw results ----- %
text(Square, Text) :-
	move(Square, Text),!;
	Text = 'N'.

draw(Result) :-
	text(a, A),text(b, B),text(c, C),
	text(d, D),text(e, E),text(f, F),
	text(g, G),text(h, H),text(i, I),
	atom_concat(A, B, Tmp),
	atom_concat(Tmp, C, Tmp1),
	atom_concat(Tmp1, D, Tmp2),
	atom_concat(Tmp2, E, Tmp3),
	atom_concat(Tmp3, F, Tmp4),
	atom_concat(Tmp4, G, Tmp5),
	atom_concat(Tmp5, H, Tmp6),
	atom_concat(Tmp6, I, Result).

drawRemi(Result) :-
	tie,
	Result = -1.

% ---------- %

addScore(Score) :-
	assertz(scores(Score)).

getScores(Scores) :-
	findall( X, scores( X ), Result ),
	bubble_sort(Result, Scores).

% sort %
bubble_sort(List,Sorted):- b_sort(List,[],Sorted).
b_sort([],Acc,Acc).
b_sort([H|T],Acc,Sorted):-bubble(H,T,NT,Max),b_sort(NT,[Max|Acc],Sorted).

bubble(X,[],[],X).
bubble(X,[Y|T],[Y|NT],Max):-X>Y,bubble(X,T,NT,Max).
bubble(X,[Y|T],[X|NT],Max):-X=<Y,bubble(Y,T,NT,Max).
% ----------- %


delete(R):-
	retractall(move(_, _)),
	R = 1.

playy(Box, Result) :-
	play(x, Box, Result).

% Player play
play(Turn, Box, Result) :-
	human(Turn),
	user_enter(Turn, Box),
	!,
	assertz(move(Box, Turn)),
	(winner(Winner) ->
	 Result = Winner,
	 delete(_)
	;
	 draw(_),
	 switch_turns(Turn, New),
	 play(New, _, Result)
	;
	 drawRemi(Result),
	 delete(_)
	),
	true.


% Computer play
play(Turn, _, Result) :-
	computer(Turn),
	enter(Square, Turn),
	!,
	assertz(move(Square, Turn)),
	(winner(Winner) ->
	 Result = Winner,
	 delete(_)
	;
	 draw(Result)
	;
	 drawRemi(Result),
	 delete(_)
	),
	true.

