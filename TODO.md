# TODO

- [ ] `model.py` 린팅 오류 해결
- [ ] `tools/math.py`: 함수 인자 개수 제한 방어

```shell

Traceback (most recent call last):
  File "/Users/mia/Github/agents/calculator/model.py", line 100, in <module>
    print(f"✅ Final Value: {execute_math(f'양의 무한대를 절반으로 나누면?')}")
                             ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mia/Github/agents/calculator/model.py", line 90, in execute_math
    result_obj = chat_with_tools(expression)
  File "/Users/mia/Github/agents/calculator/model.py", line 67, in chat_with_tools
    res = parse_and_execute(func, call.function.arguments)
  File "/Users/mia/Github/agents/calculator/model.py", line 18, in parse_and_execute
    result = func(*args) if args else None
             ~~~~^^^^^^^
TypeError: divide() missing 1 required positional argument: 'y'
```

- [ ] 프로젝트 정돈
  - [ ] `tools/math.py`
  - [ ] `model.py` 클래스 도입
  - [ ] `main.py` 엔트리 포인트
- [ ] 테스트
  - [ ] 덧셈 외 기본 테스트 추가
  - (선택) 테스트 실행 시간 개선
