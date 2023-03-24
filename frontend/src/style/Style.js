import styled from "styled-components";

export const H2 = styled.h2`
  font-size: 1.25em;
  color: #03b595;
  margin: 30px auto 10px;
  font-weight: bolder;
`;

export const P = styled.p`
  line-height: 1.75;
  margin: 0 0 1em 0;
  display: block;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
`;

export const Container = styled.div`
  max-width: 320px;
  margin: 0 auto;
  text-align: center;
  width: 100%;
`;

export const Button = styled.a`
  width: 100%;
  margin: 20px 0;
  background: #000;
  border: none;
  color: #fff;
  font-weight: bold;
  font-size: 0.75em;
  line-height: 40px;
  text-transform: uppercase;
  text-align: center;
  display: inline-block;
  font-family: "Istok Web", sans-serif;
  text-decoration: none;

  :visited {
    padding: 0;
    text-decoration: none;
  }
`;

export const Flex = styled.div`
  display: flex;
  flex-flow: row wrap;
  align-items: center;
  justify-content: space-between;
`;
