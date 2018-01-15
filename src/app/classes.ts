import { HttpHeaders } from '@angular/common/http';

export const HttpOptions = {
  headers: new HttpHeaders({'Content-Type': 'application/json'}),
}
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
  maxes: number[];
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
