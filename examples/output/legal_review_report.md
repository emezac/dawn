
            # Legal Contract Review Report

            ## Contract Topics
            ${parse_topics_json.output_data.result.topics | []}
            
            ## Legal Guidelines Referenced
            ${search_guidelines.output_data.result | 'No guidelines found'}
            
            ## Recent Legal Updates
            ${search_web.output_data.result | 'No updates found'}
            
            ## Redline Suggestions
            ${parse_redlines_json.output_data.result.redlines | []}
            
            ## Summary
            ${parse_redlines_json.output_data.result.summary | 'No summary available'}
            
            ## Status
            - Review saved to Long-Term Memory: ${save_to_ltm.output_data.success | False}
            - Report generated on: Current Date and Time
            