/* eslint-disable no-mixed-spaces-and-tabs */
import { Link } from "@mui/material";
import React, { FC } from "react";

interface Props {
  to: string;
  text: string;
}
const NavLink: FC<Props> = ({ to, text }) => {
  return (
    <>
      <Link
        href={to}
        sx={{
          textDecoration: "none",
          padding: "12px 24px",
          color: "white",
          borderRadius: "10px",
          width: "100%",
          display: "flex",
		  alignItems: 'center',
		  justifyContent: 'center',
		  border: '2px solid #4B3FD7',
		  background: 'rgba(70,59,198,0.5)',
		  transition: 'all 0.2s ease-in-out',
		  '&:hover': {
			background: "#4B3FD7",
		  }
		}}
      >
        {text}
      </Link>
    </>
  );
};
interface Props {
  to: string;
}
export default NavLink;
