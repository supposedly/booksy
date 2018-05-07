import { HttpHeaders } from '@angular/common/http';

// Just a bunch of object-type declarations.
// Got lazy as time went on and started using T<any> instead of making specific classes, lol.
// (Makes it quicker to add stuff)
export const HttpOptions = {
  headers: new HttpHeaders({'Content-Type': 'application/json'}),
};
export class NavButton {
  text: string;
  dest?: string;
}
export class SideButton {
  text: string;
  dest?: string;
  color?: string;
}
export class Role {
  perms: number[];
  limits: number[];
  locks: number[];
}
export class MediaItem {
  mid;
  type;
  genre;
  isbn;
  lid;
  title;
  author;
  price?: any;
  length?: any;
  unit?: any; // unit of length, e.g. pages or minutes
  published;
  acquired?;
  image?;
  available?;
  fines?;
}
export class MediaItemProxy {
  info: MediaItem;
}
export class Member {
  uid: string;
  lid: string;
  rid: string;
  username: string;
  fullname: string;
  email?: string;
  phone?: string;
  manages: boolean;
}
