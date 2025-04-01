import "./assets/styles.css";
import "./assets/styles.css";
import Header from "./components/Header";
import Card from "./components/Card";
import Footer from "./components/Footer";


import img1 from "/images/1img.png";
import img2 from "/images/2img.png";

const App = () => {
  return (
    <div className="container">
      <Header />
      <div className="secondsection">
        <p className="second_section_p">REVOLUTIONIZING AGRICULTURE WITH GENERATIVE AI</p>
      </div>
      <div className="thirdsection">
        <Card link="http://127.0.0.1:5000/" title="Kissan Copilot" image={img1} description="Interact with our AI to get answers to your agricultural questions." />
        <Card link="http://127.0.0.1:5000/weather" title="Agri Copilot WeatherGuard" image={img2} description=" Stay ahead of changing weather conditions with real-time updates tailored for your crops" />
      </div>
      <Footer />
    </div>
  );
};

export default App;