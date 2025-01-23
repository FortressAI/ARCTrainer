% ============================
% Aristotelian Logic with Near Enemy Detection
% ============================

% Classical Syllogism:
% If A is a subset of B, and B is a subset of C, then A is a subset of C.
syllogism(A, B, C) :- 
    premise(A, B),
    premise(B, C),
    conclusion(A, C).

% Example: All men are mortal, Socrates is a man, therefore Socrates is mortal.
premise(all_men, mortal).
premise(socrates, all_men).
conclusion(socrates, mortal).

% ============================
% Near Enemy Detection
% ============================

% A rule is considered valid only if it does not create a biased or deceptive outcome.
valid_rule(Rule) :-
    \+ biased_outcome(Rule),
    \+ near_enemy(Rule).

% Define near enemy conditions
near_enemy(Rule) :-
    appears_fair(Rule),
    hidden_bias(Rule),
    format("Warning: Rule ~w appears valid but introduces deception", [Rule]).

% Example near enemy case: Fair-sounding policy that actually discriminates
appears_fair(equal_treatment).
hidden_bias(equal_treatment) :-
    affects_unfairly(equal_treatment, marginalized_group).

% ============================
% Socratic Reasoning Hooks
% ============================

socratic_question(Rule, Why) :-
    causal_chain(Rule, Explanation),
    format("Why does ~w hold? Because ~w", [Rule, Explanation]).

validate_rule(Rule) :-
    socratic_question(Rule, Explanation),
    valid_rule(Rule),
    format("Rule ~w has passed Socratic, fairness, and near enemy checks.", [Rule]).
