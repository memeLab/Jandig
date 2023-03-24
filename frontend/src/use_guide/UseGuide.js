import styled from "styled-components";
import fill from "./fill.png";
import { H2, P, Container, Button } from "../style/Style";

const Section = styled.section`
  max-width: 300px;
  margin: 0 auto;
  margin-bottom: 20px;
  padding: 20px;
  background: url(${fill}), #e6e6e6;
`;

const BlockQuote = styled.blockquote`
  font-size: 1.1em;
  line-height: 2em;
  margin: 10px 40px;
  color: #888;
  font-style: italic;

  :before,
  :after {
    background: #03b5951a;
    max-width: 40px;
    height: 40px;
    display: block;
    margin: 0 auto -20px 0;
    content: "";
    text-align: left;
  }
  :after {
    text-align: right;
    margin: -30px 0 20px auto;
  }
`;

export const UseGuide = (props) => {
  return (
    <Section>
      <Container>
        <H2>Bem vindo ao Jandig</H2>
        <BlockQuote>
          "Uma comunidade open source de arte em realidade aumentada."
        </BlockQuote>
        <P>
          Para ver as Obras você precisa fornecer acesso a câmera do seu
          dispositivo.
        </P>
        <div>
          <Button href="/">Abrir Câmera</Button>
        </div>
      </Container>
    </Section>
  );
};
