% aristotle_logic.pl
% Aristotelian Logic with Multi-Agent Debate and Self-Contradiction Detection

% --- Debugging & Configuration ---
:- discontiguous debate_rule/3.
:- discontiguous syllogism/3.
:- discontiguous resolve_debate/3.
:- discontiguous contradicts_existing_knowledge/1.
:- multifile stored_rule/1.

% Classical Syllogism:
syllogism(A, B, C) :- premise(A, B), premise(B, C), conclusion(A, C).

% Multi-Agent Debate System
debate_rule(_Agent1, _Agent2, Rule) :-  % `_Agent1` and `_Agent2` prefixed as unused
    agent_claims(_Agent1, Rule),
    agent_challenges(_Agent2, Rule),
    resolve_debate(_Agent1, _Agent2, Rule).

resolve_debate(Agent1, Agent2, Rule) :-
    valid_causal_chain(Rule),
    format("Debate resolved in favor of rule: ~w", [Rule]).

% Self-Contradiction Detection & Resolution
detect_self_contradiction(Rule) :-
    contradicts_existing_knowledge(Rule),
    format("Warning: Rule ~w contradicts past knowledge.", [Rule]),
    resolve_conflict(Rule).

contradicts_existing_knowledge(Rule) :-
    stored_rule(ExistingRule),
    Rule \= ExistingRule,
    format("Conflict detected between ~w and ~w", [Rule, ExistingRule]).

resolve_conflict(Rule) :-
    retractall(stored_rule(_)),
    assertz(stored_rule(Rule)),
    format("Resolved conflict. New rule accepted: ~w", [Rule]).

% Example stored knowledge
stored_rule('all_men_are_mortal').
