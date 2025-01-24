% ============================
% Aristotelian Logic with Multi-Agent Debate and Self-Contradiction Detection
% ============================

% Classical Syllogism:
syllogism(A, B, C) :- premise(A, B), premise(B, C), conclusion(A, C).

% Multi-Agent Debate System
debate_rule(Agent1, Agent2, Rule) :-
    agent_claims(Agent1, Rule),
    agent_challenges(Agent2, Rule),
    resolve_debate(Agent1, Agent2, Rule).

resolve_debate(Agent1, Agent2, Rule) :-
    valid_causal_chain(Rule),
    format("Debate resolved in favor of rule: ~w", [Rule]).

% Self-Contradiction Detection
detect_self_contradiction(Rule) :-
    contradicts_existing_knowledge(Rule),
    format("Warning: Rule ~w contradicts past knowledge.", [Rule]).

contradicts_existing_knowledge(Rule) :-
    stored_rule(ExistingRule),
    Rule \= ExistingRule,
    format("Conflict detected between ~w and ~w", [Rule, ExistingRule]).

% Example stored knowledge
stored_rule('all_men_are_mortal').
