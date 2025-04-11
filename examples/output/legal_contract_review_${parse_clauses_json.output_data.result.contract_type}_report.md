# Legal Contract Review Report

## Contract Type

${parse_clauses_json.output_data.result.contract_type}

## Risk Assessment

${generate_redlines.output_data.response.risk_assessment || structure_analysis.output_data.result.risk_assessment}

## Key Clauses

${parse_clauses_json.output_data.result.key_clauses}

## Redlines

${generate_redlines.output_data.response.redlines || structure_analysis.output_data.result.redlines}

## Recommendations

${generate_redlines.output_data.response.general_recommendations || structure_analysis.output_data.result.general_recommendations}

## Legal Guidelines

${search_legal_guidelines.output_data.response}

## Legal Updates

${search_legal_web_updates.output_data.result}

