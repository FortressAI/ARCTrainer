% Domain-specific rules for the "Warfare" domain
% Now includes human-readable mappings (Controlled Natural Language - CNL)

% --- Core Warfare Concepts ---

% Defines different types of warfare.
warfare(conventional) :- involves(organized_military), uses(standard_weapons).
warfare(asymmetric) :- involves(non_state_actors), uses(unconventional_tactics).
warfare(nuclear) :- uses(nuclear_weapons), has(global_risk).
warfare(cyber) :- targets(digital_infrastructure), involves(cyber_attacks).
warfare(guerilla) :- involves(small_groups), uses(hit_and_run_tactics).

% Defines military units and roles.
military_unit(infantry) :- specializes(ground_combat), uses(small_arms).
military_unit(artillery) :- specializes(long_range_firepower), uses(heavy_weapons).
military_unit(navy) :- operates(at_sea), uses(warships).
military_unit(air_force) :- operates(in_air), uses(fighter_jets).
military_unit(special_forces) :- specializes(covert_operations), operates(behind_enemy_lines).

% Defines strategic principles.
strategy(offensive) :- seeks(territorial_gain), applies(shock_and_awe).
strategy(defensive) :- seeks(protection), applies(fortifications).
strategy(deterrence) :- prevents(conflict), relies_on(show_of_force).
strategy(psychological) :- targets(enemy_morale), involves(propoganda).

% Defines key elements of war.
element_of_war(intelligence) :- involves(spying), gathers(secret_information).
element_of_war(logistics) :- ensures(supply_lines), maintains(troop_movement).
element_of_war(diplomacy) :- aims_for(conflict_resolution), involves(treaties).

% Defines treaties and agreements.
treaty(geneva_convention) :- protects(civilians), regulates(war_conduct).
treaty(non_proliferation_treaty) :- limits(nuclear_weapons), promotes(disarmament).

% --- Query Handling ---

warfare_rules(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "warfare_query",
            intent_data: IntentData,
            parsing_logic: parse_warfare_query,
            validation_logic: validate_warfare_query,
            action_logic: handle_warfare_request
        }
    ).

% --- Query Parsing and Validation ---

% Parses a warfare-related query.
parse_warfare_query(Statement, ParsedQuery) :-
    play_language_game(
        Statement,
        game_data{
            type: "parse_query",
            parsing_logic: extract_warfare_topic,
            result_var: ParsedQuery
        }
    ).

% Validates the query's accuracy and scope.
validate_warfare_query(ParsedQuery) :-
    play_language_game(
        ParsedQuery,
        game_data{
            type: "validate_query",
            validation_logic: check_warfare_relevance
        }
    ).

% --- Handling Warfare Queries ---

% Handles user queries about warfare.
handle_warfare_request(ParsedQuery) :-
    ParsedQuery = query{topic: Topic, intent: Intent},
    warfare_topic(Topic),
    execute_warfare_intent(Intent, Topic).

% Executes actions based on user intent.
execute_warfare_intent(get_information, Topic) :-
    format("Here is general information about ~w in warfare.", [Topic]).

execute_warfare_intent(compare_strategies, Strategy1, Strategy2) :-
    format("Comparing ~w with ~w in terms of effectiveness and application.", [Strategy1, Strategy2]).

% --- Helper Logic ---

% Extracts warfare topics from queries.
extract_warfare_topic(Statement, query{topic: Topic}) :-
    member(Topic, ["conventional", "asymmetric", "nuclear", "cyber", "guerilla",
                   "intelligence", "logistics", "diplomacy", "treaties", "military_units", "strategy"]).

% Validates warfare topics.
check_warfare_relevance(Query) :-
    Query = query{topic: Topic},
    warfare_topic(Topic).

% Checks if the topic is relevant to warfare.
warfare_topic(Topic) :-
    member(Topic, ["conventional", "asymmetric", "nuclear", "cyber", "guerilla",
                   "intelligence", "logistics", "diplomacy", "treaties", "military_units", "strategy"]).

% --- Controlled Natural Language (CNL) Mappings ---

% Converts human-readable statements into Prolog rules.
cnl_to_prolog("Conventional warfare involves organized military forces and standard weapons.", warfare(conventional) :- involves(organized_military), uses(standard_weapons)).
cnl_to_prolog("Cyber warfare targets digital infrastructure and involves cyber attacks.", warfare(cyber) :- targets(digital_infrastructure), involves(cyber_attacks)).
cnl_to_prolog("Infantry specializes in ground combat and uses small arms.", military_unit(infantry) :- specializes(ground_combat), uses(small_arms)).
cnl_to_prolog("The Geneva Convention protects civilians and regulates conduct in war.", treaty(geneva_convention) :- protects(civilians), regulates(war_conduct)).

% Converts Prolog rules into human-readable statements.
prolog_to_cnl(warfare(conventional) :- involves(organized_military), uses(standard_weapons), "Conventional warfare involves organized military forces and standard weapons.").
prolog_to_cnl(warfare(cyber) :- targets(digital_infrastructure), involves(cyber_attacks), "Cyber warfare targets digital infrastructure and involves cyber attacks.").
prolog_to_cnl(military_unit(infantry) :- specializes(ground_combat), uses(small_arms), "Infantry specializes in ground combat and uses small arms.").
prolog_to_cnl(treaty(geneva_convention) :- protects(civilians), regulates(war_conduct), "The Geneva Convention protects civilians and regulates conduct in war.").

% --- Example Usage ---

% warfare_rules("What is nuclear warfare?", intent_data{primary_intent: get_information}).
% warfare_rules("Compare offensive and defensive military strategies.", intent_data{primary_intent: compare_strategies}).
% warfare_rules("What is the Geneva Convention?", intent_data{primary_intent: get_information}).
