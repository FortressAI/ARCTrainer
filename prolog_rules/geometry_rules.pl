% Domain-specific rules for geometry reasoning
% Now includes human-readable mappings (Controlled Natural Language - CNL)

% --- Geometric Knowledge Representation ---

% Defines geometric shapes and their properties.
shape(equilateral_triangle, triangle, [equal_sides, equal_angles]).
shape(isosceles_triangle, triangle, [two_equal_sides]).
shape(scalene_triangle, triangle, [all_sides_different]).
shape(right_triangle, triangle, [one_right_angle]).
shape(square, quadrilateral, [four_equal_sides, four_right_angles]).
shape(rectangle, quadrilateral, [opposite_sides_equal, four_right_angles]).
shape(circle, conic, [constant_radius]).

% --- Main Entry Point ---

geometry_rules(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "geometry_query",
            intent_data: IntentData,
            parsing_logic: parse_geometry_query,
            validation_logic: validate_geometry_query,
            action_logic: handle_geometry_request
        }
    ).

% --- Handling Geometry Queries ---

% Handles requests related to geometric properties.
handle_geometry_request(ParsedQuery) :-
    ParsedQuery = query{shape: Shape, property: Property},
    (geometric_property(Shape, Property) ->
        format("Yes, the property ~w applies to the shape ~w.", [Property, Shape])
    ;
        format("No, the property ~w does not apply to the shape ~w.", [Property, Shape])
    ).

% --- Query Parsing and Validation ---

% Parses a geometry query to extract shape and property.
parse_geometry_query(Statement, ParsedQuery) :-
    play_language_game(
        Statement,
        game_data{
            type: "parse_query",
            parsing_logic: extract_shape_and_property,
            result_var: ParsedQuery
        }
    ).

% Validates the geometry query for relevance and correctness.
validate_geometry_query(ParsedQuery) :-
    play_language_game(
        ParsedQuery,
        game_data{
            type: "validate_query",
            validation_logic: check_geometry_relevance
        }
    ).

% --- Geometry Actions ---

% Checks if a property applies to a specific shape.
geometric_property(Shape, Property) :-
    shape(Shape, _, Properties),
    member(Property, Properties).

% --- Helper Logic ---

% Extracts shape and property from a query using language games.
extract_shape_and_property(Statement, query{shape: Shape, property: Property}) :-
    % Simulated logic for parsing (replace with advanced methods if needed).
    member(Shape, ["triangle", "square", "rectangle", "circle"]),
    member(Property, ["equal_sides", "equal_angles", "right_angle", "constant_radius"]).

% Validates the shape-property pair.
check_geometry_relevance(Query) :-
    Query = query{shape: Shape, property: Property},
    shape(Shape, _, Properties),
    member(Property, Properties).

% --- Controlled Natural Language (CNL) Mappings ---

% Converts a human-readable statement into a Prolog rule.
cnl_to_prolog("A square has four equal sides and four right angles.", shape(square, quadrilateral, [four_equal_sides, four_right_angles])).
cnl_to_prolog("A right triangle has one right angle.", shape(right_triangle, triangle, [one_right_angle])).
cnl_to_prolog("A circle has a constant radius.", shape(circle, conic, [constant_radius])).

% Converts a Prolog rule into a human-readable statement.
prolog_to_cnl(shape(square, quadrilateral, [four_equal_sides, four_right_angles]), "A square has four equal sides and four right angles.").
prolog_to_cnl(shape(right_triangle, triangle, [one_right_angle]), "A right triangle has one right angle.").
prolog_to_cnl(shape(circle, conic, [constant_radius]), "A circle has a constant radius.").

% --- Example Usage ---

% geometry_rules("Does a square have four equal sides?", intent_data{primary_intent: ask_question}).
% geometry_rules("What are the properties of a right triangle?", intent_data{primary_intent: get_information}).
% geometry_rules("Is a circle defined by having a constant radius?", intent_data{primary_intent: ask_question}).
