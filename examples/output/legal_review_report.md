
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
            {'redlines': [{'clause': 'INTELLECTUAL PROPERTY', 'current_text': 'All work product developed by Consultant in performing the Services shall be the sole and exclusive property of the Company. Consultant hereby assigns all right, title, and interest in such work product to the Company.', 'suggested_text': 'All work product, including but not limited to any inventions, designs, reports, or software code, developed by Consultant in performing the Services shall be the sole and exclusive property of the Company. Consultant hereby irrevocably assigns all right, title, and interest in such work product to the Company.', 'explanation': "Clarify the scope of 'work product' and include specific examples to ensure comprehensive coverage and clarity of ownership transfer."}, {'clause': 'CONFIDENTIALITY', 'current_text': 'Consultant agrees to maintain the confidentiality of all proprietary information disclosed by the Company for a period of 5 years.', 'suggested_text': 'Consultant agrees to maintain the confidentiality of all information disclosed by the Company, including but not limited to trade secrets, business strategies, and client data, for a period of 5 years following the termination of this Agreement.', 'explanation': "Broaden the scope of protected information to encompass various types of sensitive data and specify that confidentiality obligations extend beyond the Agreement's duration."}, {'clause': 'INDEMNIFICATION', 'current_text': "Consultant agrees to indemnify and hold harmless the Company from any claims arising from Consultant's negligence or willful misconduct.", 'suggested_text': "Consultant agrees to indemnify and hold harmless the Company from any third-party claims, including but not limited to legal fees and damages, arising from Consultant's negligence or willful misconduct.", 'explanation': 'Specify the coverage of indemnification to include third-party claims and clarify the types of expenses covered by the indemnity provision.'}], 'summary': 'The suggested changes aim to enhance clarity, specificity, and comprehensiveness in defining the rights, obligations, and responsibilities of the parties regarding intellectual property, confidentiality, and indemnification.'}
            
            ## Status
            - Review saved to Long-Term Memory: ${save_to_ltm.output_data.success | False}
            - Report generated on: Current Date and Time
            