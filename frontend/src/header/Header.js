import styled from "styled-components";
import { Container, Flex } from "../style/Style";
import headerIcon from "./header_icon.png";
import langIcon from "./lang_icon.png";

const Section = styled.section`
  margin-top: 25px;
  font-size: 75%;

  @media all and (min-width: 800px) {
    margin-top: 25px;
    img {
      max-height: 75px;
      height: auto;
      margin: auto;
      transition: all 0.2s ease-in;
    }
  }
  img:hover {
    opacity: 0.7;
  }
`;

const LogoDiv = styled.div`
  text-align: left;
  height: 60px;
  width: 100%;
  float: left;
  background-image: linear-gradient(
    to top,
    #77777766,
    #77777766 50%,
    transparent 50%,
    transparent
  );
  background-position: 100% 10%;
  background-size: 100% 200%;
  a {
    display: block;
  }
  img {
    max-height: 55px;
    height: auto;
    margin: auto;
  }
  @media all and (min-width: 800px) {
    text-align: left;
    height: 95px;
    width: calc(100% - 160px);
    float: left;
    background-image: linear-gradient(
      to top,
      #77777766,
      #77777766 50%,
      transparent 50%,
      transparent
    );
    background-position: 100% 10%;
    background-size: 100% 200%;
    img {
      max-height: 75px;
      height: auto;
      margin: auto;
    }
  }
`;

const IconMenuDiv = styled(Flex)`
  height: 30px;
  text-align: right;
  flex-flow: nowrap;
  a {
    width: 30px;
    height: 30px;
    margin: 0 0 0 10px;
    display: block;
    font-size: 0;
  }
`;

const LangButtonDiv = styled.div`
  margin: 0 0 0 auto;
  a {
    background: url(${langIcon}) no-repeat;
    background-position: center center;
    background-size: contain;
    margin: 0 0 0 auto;
    font-size: 0.8em;
    font-weight: bold;
    font-family: monospace;
    text-transform: uppercase;
    color: #000;
    padding: 10px;
    height: 10px;
    width: 10px;
    line-height: 13px;
    text-align: center;
    overflow: hidden;
  }
`;

const ButtonDiv = styled.div`
  background-color: black;
  text-align: center;
  height: 25px;
  line-height: 25px;
  margin: 5px 0 0 5px;
  padding: 0px 8px;
  a {
    font-weight: bold;
    color: white;
    display: block;
    font-size: 0.75em;
  }

  @media (min-width: 800px) {
    height: 40px;
    line-height: 40px;
    width: calc(50% - 5px);
    padding-left: 0px;
    margin: 0;
    margin-left: 10px;
    a {
      font-size: 1.35em;
    }
  }
`;

const SigninButtonDiv = styled(ButtonDiv)`
  background-color: #03b595;
`;

const WelcomeDiv = styled.div`
  height: 30px;
  text-align: right;
  flex-flow: nowrap;
  height: 30px;
  font-size: 0.65em;
  overflow: hidden;
  vertical-align: bottom;
  a,
  a:visited {
    font-size: 1.25em;
    font-weight: bold;
    color: #03b595;
  }

  p {
    line-height: 45px;
  }
`;

const ConnectDiv = styled(Flex)`
  height: 30px;
  text-align: right;
  flex-flow: nowrap;
  @media all and (min-width: 800px) {
    height: 50px;
    text-align: right;
    font-size: 0.75em;
  }
`;

const AsideDiv = styled.div`
  max-width: 120px;
  margin-left: -120px;
  padding-left: 10px;
  height: 70px;
  float: right;
  background: #fff;
  @media all and (min-width: 800px) {
    max-width: 250px;
    min-width: 250px;
    height: 100px;
    margin-left: -250px;
  }
`;

const LangButton = (props) => {
  return (
    <LangButtonDiv>
      {" "}
      <a>href="#">{props.languageCode}</a>
    </LangButtonDiv>
  );
};

const SignupButton = (props) => {
  return (
    <ButtonDiv>
      <a href={props.signupUrl}>Sign up</a>
    </ButtonDiv>
  );
};

const SigninButton = (props) => {
  return (
    <SigninButtonDiv>
      {" "}
      <a href={props.signinUrl}>Sign in</a>
    </SigninButtonDiv>
  );
};

const Welcome = (props) => {
  return (
    <WelcomeDiv>
      <p>
        Welcome, <a href={props.profileUrl}>{props.username}</a>
      </p>
    </WelcomeDiv>
  );
};

const Connect = (props) => {
  return (
    <ConnectDiv>
      <SignupButton signupUrl={props.signupUrl} />
      <SigninButton siginUrl={props.singinUrl} />
    </ConnectDiv>
  );
};

const Account = (props) => {
  if (props.isAuthenticated) {
    return <Welcome profileUrl={props.profileUrl} username={props.username} />;
  } else {
    return <Connect />;
  }
};

const IconMenu = (props) => {
  return (
    <IconMenuDiv>
      <LangButton />
    </IconMenuDiv>
  );
};

export const Logo = (props) => {
  return (
    <LogoDiv>
      <a href={props.href}>
        <img alt="Jandig Logo" src={headerIcon} />
      </a>
    </LogoDiv>
  );
};

export const Header = (props) => {
  return (
    <Section>
      <Container>
        <Logo href="/"></Logo>
        <AsideDiv>
          <IconMenu />
          <Account isAuthenticated={props.isAuthenticated} />
        </AsideDiv>
      </Container>
    </Section>
  );
};
