import { HttpHeaders } from '@angular/common/http';

export const httpOptions = {
  headers: new HttpHeaders({'Content-Type': 'application/json'});
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
export class ManagePageButton {
  text: string;
  dest?: string;
}
export class MediaItem {
  id: string;
  type: string;
  isbn: string;
  lid: string;
  title: string;
  author: string;
  published: string;
  acquired: string;
}
export class PersonalItem {
  mid: string;
  lid: string;
  type: string;
  isbn: string;
  title: string;
  author: string;
  published: string;
  acquired: string;
  issuedto: string;
  due: string;
  fines: string;
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