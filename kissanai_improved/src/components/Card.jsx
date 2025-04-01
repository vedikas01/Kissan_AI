import "../assets/styles.css";

const Card = ({ link, title, image, description }) => {
  return (
    <div className="card">
      <div className="upper">
        <a href={link} className="class1">
          {title}
        </a>
      </div>
      <div className="lower">
        <img src={image} alt={title} className="cardimg" />
        <div className="overlay-text">{description}</div>
      </div>
    </div>
  );
};

export default Card;
