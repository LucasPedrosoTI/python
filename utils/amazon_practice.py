def search_suggestions(repository: list[str], customer_query: str) -> list[list[str]]: 
  returnValue: list(list(str)) = []
  sorted_repo = sorted(repository)
  partial_query = ''
  for i, letter in enumerate(customer_query):
    partial_query += letter
    if i < 1:
      continue
    partial_list = []
    for word in sorted_repo:
      if len(partial_list) == 3:
        break
      if partial_query in word:
        partial_list.append(word)
    
    returnValue.append(partial_list)

  return returnValue

print(search_suggestions(['mobile', 'mouse', 'moneypot', 'monitor', 'mousepad'], 'mouse'))