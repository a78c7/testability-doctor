pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[test]
fn it_works() {
    assert_eq!(add(2, 2), 4);
}
